"""
Tests for sft.py training script.

Tests template consistency between conversion script and SFT training,
ensuring DataCollatorForCompletionOnlyLM works correctly with Gemma format.
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from convert_to_gemma_format import parse_qwen_text, convert_to_gemma_format


# Sample Qwen-formatted text for testing
SAMPLE_QWEN_TEXT = """<|im_start|>system
You are a helpful math tutor.<|im_end|>
<|im_start|>user
What is 2 + 2?<|im_end|>
<|im_start|>think
This is a simple addition problem.
2 + 2 = 4<|im_start|>answer
The answer is 4.<|im_end|>"""


class TestTemplateConsistency:
    """Tests verifying sft.py templates match conversion output."""

    def test_response_template_in_converted_output(self):
        """Verify the response_template appears in converted Gemma text."""
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        # The response_template from sft.py
        response_template = "<start_of_turn>model\n"

        assert response_template in gemma_text, (
            f"Response template '{response_template}' not found in converted text"
        )

    def test_instruction_template_in_converted_output(self):
        """Verify the instruction_template appears in converted Gemma text."""
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        # The instruction_template from sft.py
        instruction_template = "<start_of_turn>user"

        assert instruction_template in gemma_text, (
            f"Instruction template '{instruction_template}' not found in converted text"
        )

    def test_no_bos_token_in_converted_text(self):
        """Verify converted text does NOT contain <bos> (tokenizer adds it)."""
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        assert "<bos>" not in gemma_text, (
            "Converted text should not contain <bos> - tokenizer adds it automatically"
        )


# Check if transformers and trl are available for collator test
try:
    import transformers
    import trl

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="transformers/trl not installed")
class TestDataCollator:
    """Test DataCollatorForCompletionOnlyLM masks instructions correctly."""

    def test_collator_masks_instruction_tokens(self):
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
