import os
from dataclasses import dataclass, asdict
import warnings
from datasets import load_dataset
import transformers
import trl
import logging

warnings.filterwarnings("ignore", category=FutureWarning)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@dataclass
class TrainingConfig:
    model_name: str = (
        "Qwen/Qwen2.5-1.5B-Instruct"  # original: "Qwen/Qwen2.5-32B-Instruct"
    )
    block_size: int = 2048  # Original: 32768
    dagger: bool = False
    small_sample: bool = True  # Flag to train on a small sample
    train_file_path: str = "simplescaling/s1K_tokenized"

    def __post_init__(self):
        os.environ["WANDB_MODE"] = "disabled"  # Prevents wandb from running


def train():
    # Parsing input
    parser = transformers.HfArgumentParser((TrainingConfig, trl.SFTConfig))
    config, args = parser.parse_args_into_dataclasses()
    log_config = {**asdict(config), **asdict(args)}
    logging.info(f"Training config: {log_config}")

    # Loading model with auto device mapping
    kwargs = {
        "device_map": "auto",
        "torch_dtype": "auto",
        "use_cache": False,  # Avoid caching for training
    }

    model = transformers.AutoModelForCausalLM.from_pretrained(
        config.model_name, **kwargs
    )

    model.gradient_checkpointing_enable()  # Original didn't have this

    dataset = load_dataset(config.train_file_path)

    # Select a small sample for testing purposes if the flag is set
    if config.small_sample:
        dataset["train"] = dataset["train"].select(range(10))  # Select first 10 samples
        if "test" in dataset:
            dataset["test"] = dataset["test"].select(
                range(10)
            )  # Select first 10 samples

    # Setting up tokenizer
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        config.model_name, use_fast=True
    )

    # Setting pad tokens
    instruction_template = "<|im_start|>user"
    response_template = "<|im_start|>assistant\n"
    tokenizer.pad_token = "<|fim_pad|>"

    # Only compute loss over assistant responses
    # Verified that it precisely starts where the thinking tokens start and ends with the first pad token
    # via labels being set to -100
    collator = trl.DataCollatorForCompletionOnlyLM(
        instruction_template=instruction_template,
        response_template=response_template,
        tokenizer=tokenizer,
        mlm=False,
    )
    args.dataset_text_field = "text"
    args.max_seq_length = config.block_size
    args.per_device_train_batch_size = 1  # Original didn't have this

    trainer = trl.SFTTrainer(
        model,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"] if "test" in dataset else dataset["train"],
        args=args,
        data_collator=collator,
    )

    trainer.train()
    trainer.save_model(output_dir=args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    trainer.accelerator.wait_for_everyone()


if __name__ == "__main__":
    #    os.environ["PYTORCH_MPS_HIGH_WATERMARK_RATIO"] = "0.0"
    train()
