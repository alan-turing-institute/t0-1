"""
Tests for sft.py training script.

Tests that DataCollatorForCompletionOnlyLM works correctly with Gemma format.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from convert_to_gemma_format import parse_qwen_text, convert_to_gemma_format

# Check if transformers and trl are available
try:
    import transformers
    import trl

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


SAMPLE_QWEN_TEXT = """<|im_start|>system
You are a helpful math tutor.<|im_end|>
<|im_start|>user
What is 2 + 2?<|im_end|>
<|im_start|>think
This is a simple addition problem.
2 + 2 = 4<|im_start|>answer
The answer is 4.<|im_end|>"""


@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="transformers/trl not installed")
def test_collator_masks_instruction_tokens():
    """Verify DataCollator sets labels to -100 for instruction tokens."""
    try:
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            "google/gemma-3-270m-it", use_fast=True
        )
    except Exception as e:
        pytest.skip(f"Could not load Gemma tokenizer: {e}")

    tokenizer.pad_token = tokenizer.pad_token or "<pad>"

    collator = trl.DataCollatorForCompletionOnlyLM(
        instruction_template="<start_of_turn>user",
        response_template="<start_of_turn>model\n",
        tokenizer=tokenizer,
        mlm=False,
    )

    # Convert sample text
    components = parse_qwen_text(SAMPLE_QWEN_TEXT)
    gemma_text = convert_to_gemma_format(components)

    # Tokenize
    tokenized = tokenizer(
        gemma_text, truncation=True, max_length=512, return_tensors="pt"
    )

    # Apply collator
    batch = [{"input_ids": tokenized["input_ids"][0]}]
    collated = collator(batch)

    labels = collated["labels"][0].tolist()

    # Count masked vs unmasked labels
    masked_count = sum(1 for label in labels if label == -100)
    unmasked_count = sum(1 for label in labels if label != -100)

    assert masked_count > 0, "Should have some masked (instruction) tokens"
    assert unmasked_count > 0, "Should have some unmasked (response) tokens"
