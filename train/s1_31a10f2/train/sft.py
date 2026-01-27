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


@dataclass
class TrainingConfig:
    model_name: str = field(default="Qwen/Qwen2.5-32B-Instruct")
    block_size: int = field(default=32768)
    wandb_project: Optional[str] = field(default="t0")
    wandb_entity: Optional[str] = field(default="alan-turing-institute")
    train_file_path: Optional[str] = field(default='simplescaling/s1K-1.1_tokenized')
    dagger: bool = field(default=False)
    lora: bool = field(default=False)

    def __post_init__(self):
        os.environ['WANDB_PROJECT'] = self.wandb_project
        os.environ['WANDB_ENTITY'] = self.wandb_entity


def load_data(path_or_id: str):
    """
    Robustly loads a dataset from a local path (prioritising arrow format)
    or a Hugging Face Hub ID.
    """

    # Check if the path is a local directory
    if os.path.isdir(path_or_id):
        logging.info(f"Path '{path_or_id}' exists locally. Attempting `load_from_disk`...")
        try:
            dataset = load_from_disk(path_or_id)
            logging.info("Successfully loaded dataset via `load_from_disk`.")
            return dataset
        except Exception as e:
            logging.warning(f"`load_from_disk` failed with error: {e}")
            logging.info("Falling back to `load_dataset` for local files (JSON/CSV/Parquet)...")

    # Fallback: Use load_dataset
    # This covers:
    #   a) Hugging Face Hub IDs (e.g., "meta-llama/Llama-2-7b-hf")
    #   b) Local folders containing raw data (json, csv) that aren't Arrow archives
    #   c) Local Arrow archives where load_from_disk crashed (e.g., metadata mismatch)
    try:
        dataset = load_dataset(path_or_id)
        logging.info(f"Successfully loaded dataset via `load_dataset`.")
        return dataset
    except Exception as e:
        logging.error(f"Failed to load dataset from '{path_or_id}'.")
        raise e


def train():
    # parsing input
    parser = transformers.HfArgumentParser((TrainingConfig, trl.SFTConfig))
    config, args = parser.parse_args_into_dataclasses()
    log_config = {**asdict(config), **asdict(args)}
    logging.info(f"Training config: {log_config}")

    # loading model
    model_config = transformers.AutoConfig.from_pretrained(config.model_name)
    model_config.use_cache = False 

    kwargs = {} 
    if "70B" in config.model_name:
        model_config.attn_implementation = "flash_attention_2"
        kwargs.update({
            "device_map": "auto", 
            "torch_dtype": "auto",
        })
    elif "gemma" in config.model_name.lower():
        logging.info("Forcing Eager attention and BF16 for Gemma.")
        model_config.attn_implementation = "eager"
        kwargs.update({
            "torch_dtype": "auto",
        })
    else:
        pass

    logging.info(f"Loading model with updated config...")
    model = transformers.AutoModelForCausalLM.from_pretrained(
        config.model_name, 
        config=model_config,
        **kwargs
    )

    # applying LoRA if specified
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

    # loading dataset
    dataset = load_data(config.train_file_path)

    # setting up trainer
    tokenizer = transformers.AutoTokenizer.from_pretrained(config.model_name, use_fast=True)
    
    if "llama" in config.model_name.lower():
        instruction_template = "<|start_header_id|>user<|end_header_id|>"
        response_template = "<|start_header_id|>assistant<|end_header_id|>\n\n"
        # Use a token that is never used
        tokenizer.pad_token = "<|reserved_special_token_5|>"
    elif "Qwen" in config.model_name:
        instruction_template = "<|im_start|>user"
        response_template = "<|im_start|>assistant\n"
        # Use a token that is never used
        tokenizer.pad_token = "<|fim_pad|>"
    elif "gemma" in config.model_name.lower():
        instruction_template = "<start_of_turn>user"
        response_template = "<start_of_turn>model\n"
        tokenizer.pad_token = tokenizer.pad_token or "<pad>"
    else:
        raise ValueError(
            f"Unsupported model: {config.model_name}. "
            "Supported models: Llama, Qwen, Gemma"
        )

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

    # hardcoding gradient checkpointing
    args.gradient_checkpointing = True
    args.gradient_checkpointing_kwargs = {"use_reentrant": False}
    logging.info(f"Gradient checkpointing set to {args.gradient_checkpointing}")
    logging.info(f"Gradient checkpointing kwargs set to {args.gradient_checkpointing_kwargs}")

    if "gemma" in config.model_name.lower():
        args.use_liger_kernel = True

    trainer = trl.SFTTrainer(
        model,
        train_dataset=dataset['train'],
        eval_dataset=dataset['test'] if 'test' in dataset else dataset['train'],
        args=args,
        data_collator=collator,
        peft_config=lora_config,
    )

    if "gemma" in config.model_name.lower():
        # CRITICAL: Prevent evaluation loop from trying to cast HybridCache to float
        trainer.args.ignore_keys_for_eval = ["past_key_values"]
        # 1. Disable in main config
        model.config.use_cache = False
        # 2. Disable in generation_config (often the culprit during eval)
        if hasattr(model, "generation_config") and model.generation_config is not None:
            model.generation_config.use_cache = False
        # 3. If using LoRA/PEFT, the config might be nested. Fix the base model too.
        if hasattr(model, "base_model") and hasattr(model.base_model, "config"):
            model.base_model.config.use_cache = False

    trainer.train()

    logging.info("Training completed. Saving model and tokenizer...")
    trainer.save_model(output_dir=args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    trainer.accelerator.wait_for_everyone()


if __name__ == "__main__":
    train()
