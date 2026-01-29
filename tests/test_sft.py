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

from apply_chat_template import process_cot_example, PROMPT, RESPONSE, SYSTEM_PROMPT

# Check if transformers and trl are available
try:
    import transformers
    import trl

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


SAMPLE_EXAMPLE = {
    SYSTEM_PROMPT: "You are a helpful math tutor.",
    PROMPT: "What is 2 + 2?",
    RESPONSE: "<think>This is a simple addition problem.\n2 + 2 = 4</think>The answer is 4.",
    "conditions_title": "test",
}

SAMPLE_NATIVE_REASONING_EXAMPLE = {
    SYSTEM_PROMPT: "You are a clinical AI assistant.",
    PROMPT: "Patient has a headache and fever.",
    RESPONSE: "(Migraine, Self-care)",
    "rag_reasoning_content": "The patient presents with headache and fever. Based on the context, this is most likely a migraine.",
    "conditions_title": "Migraine",
}


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

    # Convert sample text using apply_chat_template
    result = process_cot_example(SAMPLE_EXAMPLE, tokenizer, "google/gemma-3-270m-it")
    gemma_text = result["text"]

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


@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="transformers/trl not installed")
def test_native_reasoning_content():
    """Verify process_cot_example handles native reasoning_content field."""
    try:
        tokenizer = transformers.AutoTokenizer.from_pretrained(
            "google/gemma-3-270m-it", use_fast=True
        )
    except Exception as e:
        pytest.skip(f"Could not load Gemma tokenizer: {e}")

    result = process_cot_example(
        SAMPLE_NATIVE_REASONING_EXAMPLE, tokenizer, "google/gemma-3-270m-it"
    )
    assert result is not None, "process_cot_example should not return None for native reasoning"
    text = result["text"]
    # Should contain the reasoning wrapped in <think> tags (Gemma format)
    assert "<think>" in text
    assert "</think>" in text
    # The answer should appear after </think>
    assert "(Migraine, Self-care)" in text
    # The native reasoning content should be inside <think> tags
    assert "most likely a migraine" in text
