"""
Tests for convert_to_gemma_format script.

Tests the conversion of Qwen-formatted training data to Gemma format.
"""

import sys
from pathlib import Path

# Add scripts directory to path to import the module
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from convert_to_gemma_format import parse_qwen_text, convert_to_gemma_format


class TestConversion:
    """Essential tests for Qwen to Gemma format conversion."""

    def test_parse_qwen_text(self):
        """Test parsing a complete Qwen-formatted text."""
        qwen_text = """<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
What is 2+2?<|im_end|>
<|im_start|>think
Let me calculate this simple addition.
2 + 2 = 4<|im_start|>answer
The answer is 4.<|im_end|>"""

        result = parse_qwen_text(qwen_text)

        assert result["system"] == "You are a helpful assistant."
        assert result["user"] == "What is 2+2?"
        assert "Let me calculate this simple addition" in result["thinking"]
        assert "2 + 2 = 4" in result["thinking"]
        assert result["answer"] == "The answer is 4."

    def test_convert_to_gemma_format(self):
        """Test conversion produces correct Gemma format structure."""
        components = {
            "system": "You are helpful.",
            "user": "What is AI?",
            "thinking": "AI stands for Artificial Intelligence.",
            "answer": "AI is artificial intelligence.",
        }

        result = convert_to_gemma_format(components)

        # Check structure
        assert result.startswith("<start_of_turn>user\n")
        assert "<end_of_turn>\n<start_of_turn>model\n" in result
        assert result.endswith("<end_of_turn>")

        # Check content is present
        assert "You are helpful." in result
        assert "What is AI?" in result
        assert "[Thinking: AI stands for Artificial Intelligence.]" in result
        assert "[Answer: AI is artificial intelligence.]" in result

        # No BOS token (tokenizer adds it)
        assert "<bos>" not in result

    def test_full_pipeline(self):
        """Test complete pipeline from Qwen text to Gemma format."""
        qwen_text = """<|im_start|>system
You are a math tutor.<|im_end|>
<|im_start|>user
What is 5 * 6?<|im_end|>
<|im_start|>think
5 times 6 equals 30.<|im_start|>answer
5 * 6 = 30<|im_end|>"""

        # Parse
        components = parse_qwen_text(qwen_text)
        assert components["system"] == "You are a math tutor."
        assert components["user"] == "What is 5 * 6?"
        assert components["thinking"] == "5 times 6 equals 30."
        assert components["answer"] == "5 * 6 = 30"

        # Convert
        gemma_text = convert_to_gemma_format(components)

        # Verify Gemma format
        assert gemma_text.startswith("<start_of_turn>user\n")
        assert "You are a math tutor." in gemma_text
        assert "What is 5 * 6?" in gemma_text
        assert "[Thinking: 5 times 6 equals 30.]" in gemma_text
        assert "[Answer: 5 * 6 = 30]" in gemma_text
        assert gemma_text.endswith("<end_of_turn>")


# =============================================================================
# Sanity check on real data (skipped if datasets don't exist)
# =============================================================================

import random
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
ORIGINAL_DATASET = (
    PROJECT_ROOT / "data" / "reasoning_traces" / "2k-deepseek-traces-k5_qwen_summarised_data"
)
CONVERTED_DATASET = (
    PROJECT_ROOT / "data" / "reasoning_traces" / "2k-deepseek-traces-k5_qwen_summarised_data_gemma"
)

datasets_exist = ORIGINAL_DATASET.exists() and CONVERTED_DATASET.exists()


@pytest.mark.skipif(not datasets_exist, reason="Dataset files not found")
def test_real_data_conversion():
    """Sanity check: verify a few real samples convert correctly."""
    from datasets import load_from_disk

    original = load_from_disk(str(ORIGINAL_DATASET))
    converted = load_from_disk(str(CONVERTED_DATASET))

    # Check same number of samples
    assert len(original["train"]) == len(converted["train"])

    # Spot-check 5 random samples
    indices = random.sample(range(len(original["train"])), min(5, len(original["train"])))

    for idx in indices:
        original_text = original["train"][idx]["text"]
        converted_text = converted["train"][idx]["text"]

        # Parse original and reconvert
        components = parse_qwen_text(original_text)
        expected = convert_to_gemma_format(components)

        assert converted_text == expected, f"Sample {idx}: conversion mismatch"

        # Verify Gemma format structure
        assert converted_text.startswith("<start_of_turn>user\n")
        assert "<start_of_turn>model\n" in converted_text
        assert converted_text.endswith("<end_of_turn>")
        assert "<bos>" not in converted_text
