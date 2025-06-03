import os
from dataclasses import dataclass, field, asdict
from typing import Optional
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from datasets import load_dataset, load_from_disk
import transformers
import trl
from peft import LoraConfig, get_peft_model
import torch


@dataclass
class TrainingConfig:
    model_name: str = field(default="Qwen/Qwen2.5-32B-Instruct")
    block_size: int = field(default=32768)
    wandb_project: Optional[str] = field(default="s1")
    wandb_entity: Optional[str] = field(default="hashimoto-group")
    train_file_path: Optional[str] = field(default='simplescaling/s1K_tokenized')
    dagger: bool = field(default=False)
    lora: bool = field(default=False)

    def __post_init__(self):
        os.environ['WANDB_PROJECT'] = self.wandb_project
        os.environ['WANDB_ENTITY'] = self.wandb_entity


class MemoryLoggingSFTTrainer(trl.SFTTrainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_grad_mem = 0

    def training_step(self, *args, **kwargs):
        loss = super().training_step(*args, **kwargs)

        # Log gradient memory after backward
        grad_bytes = sum(
            p.grad.numel() * p.grad.element_size()
            for p in self.model.parameters()
            if p.grad is not None
        )

        grad_mem_mb = grad_bytes / (1024 ** 3)

        current_allocated = torch.cuda.memory_allocated() / (1024 ** 3)
        current_reserved = torch.cuda.memory_reserved() / (1024 ** 3)

        logging.info(f"[During Training] Gradient memory: {grad_mem_mb:.2f} GB")
        logging.info(f"[During Training] Allocated: {current_allocated:.2f} GB | Reserved: {current_reserved:.2f} GB")

        if grad_mem_mb > self.max_grad_mem:
            self.max_grad_mem = grad_mem_mb

        return loss


def train():
    # parsing input
    parser = transformers.HfArgumentParser((TrainingConfig, trl.SFTConfig))
    config, args = parser.parse_args_into_dataclasses()
    log_config = {**asdict(config), **asdict(args)}
    logging.info(f"Training config: {log_config}")

    # loading model
    kwargs = {}
    if "70B" in config.model_name:
        # Removed "low_cpu_mem_usage": True, for 70B, since by default we are in FSDP,
        # it's more efficient to do  "cpu_ram_efficient_loading": true, in fsdp_config.json
        kwargs = {"device_map": "auto", "torch_dtype": "auto",
                  "attn_implementation": "flash_attention_2", "use_cache": False}
    else:
        kwargs = {"use_cache": False}

    model = transformers.AutoModelForCausalLM.from_pretrained(config.model_name, **kwargs)

    lora_config = None
    if config.lora:
        lora_config_path = "train/lora_config.json"

        if os.path.exists(lora_config_path):
            with open(lora_config_path, "r") as f:
                lora_config = LoraConfig(**LoraConfig.from_json_file(lora_config_path))
        else:
            logging.error(f"LoRA configuration file not found at {lora_config_path}.")
            raise FileNotFoundError(f"LoRA configuration file not found at {lora_config_path}.")

        logging.info("LoRA configuration loaded successfully.")

        model = get_peft_model(model, lora_config)

        logging.info("LoRA model loaded successfully.")
        logging.info(f"LoRA config: {lora_config}")
        logging.info("LoRA model parameters:")
        model.print_trainable_parameters()

    model_param_mem = sum(p.numel() * p.element_size() for p in model.parameters()) / 1024**3
    logging.info(f"Model Parameters: {model_param_mem:.2f} GB")

    try:
        dataset = load_dataset(config.train_file_path)
    except Exception as e:
        logging.error(f"Error loading dataset: {e}")
        logging.info("Attempting to load dataset from disk...")
        dataset = load_from_disk(config.train_file_path)

    # setting up trainer
    tokenizer = transformers.AutoTokenizer.from_pretrained(config.model_name, use_fast=True)
    if "Llama" in config.model_name:
        instruction_template = "<|start_header_id|>user<|end_header_id|>"
        response_template = "<|start_header_id|>assistant<|end_header_id|>\n\n"
        # Use a token that is never used
        tokenizer.pad_token = "<|reserved_special_token_5|>"
    elif "Qwen" in config.model_name:
        instruction_template = "<|im_start|>user"
        response_template = "<|im_start|>assistant\n"
        # Use a token that is never used
        tokenizer.pad_token = "<|fim_pad|>"

    # Only compute loss over assistant responses
    # Verified that it precisely starts where the thinking tokens start and ends with the first pad token
    # via labels being set to -100
    collator = trl.DataCollatorForCompletionOnlyLM(
        instruction_template=instruction_template,
        response_template=response_template,
        tokenizer=tokenizer,
        mlm=False
    )

    args.dataset_text_field = 'text'
    args.max_seq_length = config.block_size
    args.gradient_checkpointing = True
    args.gradient_checkpointing_kwargs = {"use_reentrant": False}
    trainer = MemoryLoggingSFTTrainer(
        model,
        train_dataset=dataset['train'],
        eval_dataset=dataset['test'] if 'test' in dataset else dataset['train'],
        args=args,
        data_collator=collator,
        peft_config=lora_config,
    )

    torch.cuda.reset_peak_memory_stats()
    logging.info("Starting training...")

    trainer.train()

    peak_memory = torch.cuda.max_memory_allocated() / (1024 ** 3)  # in GB
    logging.info(f"Peak GPU memory allocated: {peak_memory:.2f} GB")

    if hasattr(trainer, "optimizer"):
        opt_state_mem = sum(
            p.numel() * p.element_size()
            for state in trainer.optimizer.state.values()
            for p in state.values()
            if torch.is_tensor(p)
        ) / 1024**3
        logging.info(f"Optimizer State: {opt_state_mem:.2f} GB")
    else:
        logging.warning("Optimizer not found on trainer; skipping optimizer memory calculation.")
        opt_state_mem = 0

    grad_mem = trainer.max_grad_mem
    logging.info(f"Gradients: {grad_mem:.2f} GB")

    total_known = model_param_mem + grad_mem + opt_state_mem
    residual_mem = peak_memory - total_known
    logging.info(f"Residual (activations + buffers + fragmentation): {residual_mem:.2f} GB")

    logging.info("Training completed. Saving model and tokenizer...")
    trainer.save_model(output_dir=args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    trainer.accelerator.wait_for_everyone()

    logging.info("Training completed.")


if __name__ == "__main__":
    train()
