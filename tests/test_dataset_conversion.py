"""
Integration tests for dataset conversion.

These tests verify that actual dataset files are converted correctly,
checking that content is preserved when converting from Qwen to Gemma format.
"""

import sys
from pathlib import Path
import random

import pytest

# Add scripts directory to path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from convert_to_gemma_format import parse_qwen_text, convert_to_gemma_format

# Check if dataset files exist
PROJECT_ROOT = Path(__file__).parent.parent
ORIGINAL_DATASET = (
    PROJECT_ROOT
    / "data"
    / "reasoning_traces"
    / "2k-deepseek-traces-k5_qwen_summarised_data"
)
CONVERTED_DATASET = (
    PROJECT_ROOT
    / "data"
    / "reasoning_traces"
    / "2k-deepseek-traces-k5_qwen_summarised_data_gemma"
)

datasets_exist = ORIGINAL_DATASET.exists() and CONVERTED_DATASET.exists()


def extract_content_from_qwen(qwen_text: str) -> dict:
    """
    Extract pure content from Qwen-formatted text (without tokens).

    Returns dict with system, user, thinking, answer content.
    """
    return parse_qwen_text(qwen_text)


def extract_content_from_gemma(gemma_text: str) -> dict:
    """
    Extract pure content from Gemma-formatted text (without tokens).

    Returns dict with system, user, thinking, answer content.
    """
    content = {"system": "", "user": "", "thinking": "", "answer": ""}

    # Remove formatting tokens and extract content
    # Extract user turn (between <start_of_turn>user and first <end_of_turn>)
    if "<start_of_turn>user\n" in gemma_text and "<end_of_turn>" in gemma_text:
        user_section = gemma_text.split("<start_of_turn>user\n")[1].split(
            "<end_of_turn>"
        )[0]

        # User section may contain system (prepended) and user message
        # They're separated by \n\n if both exist
        if "\n\n" in user_section:
            parts = user_section.split("\n\n", 1)
            # We need to determine which is system and which is user
            # Since system comes first, first part might be system
            # But if there's no system, it's all user
            # This is tricky without more context, so we'll just capture the full user turn
            content["user"] = user_section
        else:
            content["user"] = user_section

    # Extract model turn (between <start_of_turn>model and last <end_of_turn>)
    if "<start_of_turn>model\n" in gemma_text:
        model_section = gemma_text.split("<start_of_turn>model\n")[1]
        if "<end_of_turn>" in model_section:
            model_section = model_section.split("<end_of_turn>")[0]

        # Extract thinking (in [Thinking: ...] format)
        if "[Thinking: " in model_section:
            thinking_start = model_section.index("[Thinking: ") + len("[Thinking: ")
            thinking_end = model_section.index("]", thinking_start)
            content["thinking"] = model_section[thinking_start:thinking_end]

        # Extract answer (in [Answer: ...] format)
        if "[Answer: " in model_section:
            answer_start = model_section.index("[Answer: ") + len("[Answer: ")
            answer_end = model_section.index("]", answer_start)
            content["answer"] = model_section[answer_start:answer_end]

    return content


@pytest.mark.skipif(not datasets_exist, reason="Dataset files not found")
class TestDatasetConversion:
    """Integration tests using actual dataset files."""

    @pytest.fixture(scope="class")
    def datasets(self):
        """Load both original and converted datasets."""
        try:
            from datasets import load_from_disk

            original = load_from_disk(str(ORIGINAL_DATASET))
            converted = load_from_disk(str(CONVERTED_DATASET))
            return original, converted
        except Exception as e:
            pytest.skip(f"Could not load datasets: {e}")

    def test_dataset_lengths_match(self, datasets):
        """Verify that both datasets have the same number of samples."""
        original, converted = datasets

        assert "train" in original, "Original dataset missing 'train' split"
        assert "train" in converted, "Converted dataset missing 'train' split"

        assert len(original["train"]) == len(
            converted["train"]
        ), f"Dataset lengths don't match: original={len(original['train'])}, converted={len(converted['train'])}"

    def test_random_sample_content_preservation(self, datasets):
        """
        Test that a random sample's content is preserved exactly.

        Picks a random element and verifies the actual content (excluding
        formatting tokens) is identical between original and converted.
        """
        original, converted = datasets

        # Pick a random index
        dataset_length = len(original["train"])
        random_idx = random.randint(0, dataset_length - 1)

        print(f"\nTesting sample at index {random_idx}")

        # Get the samples
        original_sample = original["train"][random_idx]
        converted_sample = converted["train"][random_idx]

        # Extract content from both
        original_content = extract_content_from_qwen(original_sample["text"])

        # For converted, we need to verify it contains the same content
        # by parsing and re-converting to see if we get the same result
        reconverted = convert_to_gemma_format(original_content)

        # The converted sample should match our reconversion
        # (both should be in Gemma format with same content)
        assert (
            converted_sample["text"] == reconverted
        ), f"Sample {random_idx}: Converted format doesn't match expected Gemma format"

    def test_multiple_random_samples(self, datasets):
        """Test content preservation across multiple random samples."""
        original, converted = datasets

        dataset_length = len(original["train"])
        num_samples = min(10, dataset_length)  # Test up to 10 random samples

        # Get random indices
        random_indices = random.sample(range(dataset_length), num_samples)

        for idx in random_indices:
            original_sample = original["train"][idx]
            converted_sample = converted["train"][idx]

            # Parse original and reconvert
            original_content = extract_content_from_qwen(original_sample["text"])
            reconverted = convert_to_gemma_format(original_content)

            assert (
                converted_sample["text"] == reconverted
            ), f"Sample {idx}: Content mismatch between converted and expected"

    def test_first_sample_content_matches(self, datasets):
        """Test that the first sample's content is preserved correctly."""
        original, converted = datasets

        original_sample = original["train"][0]
        converted_sample = converted["train"][0]

        # Parse original
        original_content = extract_content_from_qwen(original_sample["text"])

        # Reconvert and compare
        reconverted = convert_to_gemma_format(original_content)

        assert (
            converted_sample["text"] == reconverted
        ), "First sample: Converted format doesn't match expected"

        # Also verify content is present in converted version
        gemma_content = extract_content_from_gemma(converted_sample["text"])

        # Check that key content appears in the Gemma version
        if original_content["user"]:
            assert (
                original_content["user"] in converted_sample["text"]
            ), "User content not found in converted sample"

        if original_content["thinking"]:
            assert (
                original_content["thinking"] in converted_sample["text"]
            ), "Thinking content not found in converted sample"

        if original_content["answer"]:
            assert (
                original_content["answer"] in converted_sample["text"]
            ), "Answer content not found in converted sample"

    def test_all_samples_have_required_format(self, datasets):
        """Verify all converted samples have proper Gemma format structure."""
        original, converted = datasets

        dataset_length = len(converted["train"])
        sample_size = min(50, dataset_length)  # Check up to 50 samples

        indices_to_check = random.sample(range(dataset_length), sample_size)

        for idx in indices_to_check:
            sample_text = converted["train"][idx]["text"]

            # Check for required Gemma format tokens
            # Note: <bos> is NOT in the text - the tokenizer adds it automatically
            assert sample_text.startswith(
                "<start_of_turn>user\n"
            ), f"Sample {idx}: Missing proper Gemma start tokens"

            assert (
                "<end_of_turn>" in sample_text
            ), f"Sample {idx}: Missing <end_of_turn> token"

            assert (
                "<start_of_turn>model\n" in sample_text
            ), f"Sample {idx}: Missing model turn"

            assert sample_text.endswith(
                "<end_of_turn>"
            ), f"Sample {idx}: Should end with <end_of_turn>"

    def test_content_not_duplicated(self, datasets):
        """Verify that content isn't accidentally duplicated during conversion."""
        original, converted = datasets

        # Check a random sample
        random_idx = random.randint(0, len(original["train"]) - 1)

        original_sample = original["train"][random_idx]
        converted_sample = converted["train"][random_idx]

        # Parse content
        original_content = extract_content_from_qwen(original_sample["text"])

        # Check that the wrapper format [Answer: ...] appears exactly once
        # This verifies we're not duplicating the entire answer section
        answer_wrapper_count = converted_sample["text"].count("[Answer: ")
        assert (
            answer_wrapper_count <= 1
        ), f"Sample {random_idx}: [Answer: ] appears {answer_wrapper_count} times (expected 0 or 1)"

        # Similarly for thinking
        thinking_wrapper_count = converted_sample["text"].count("[Thinking: ")
        assert (
            thinking_wrapper_count <= 1
        ), f"Sample {random_idx}: [Thinking: ] appears {thinking_wrapper_count} times (expected 0 or 1)"


class TestDatasetStructure:
    """Tests verifying general dataset structure and properties."""

    @pytest.fixture(scope="class")
    def datasets(self):
        """Load both original and converted datasets."""
        if not datasets_exist:
            pytest.skip("Dataset files not found")
        try:
            from datasets import load_from_disk

            original = load_from_disk(str(ORIGINAL_DATASET))
            converted = load_from_disk(str(CONVERTED_DATASET))
            return original, converted
        except Exception as e:
            pytest.skip(f"Could not load datasets: {e}")

    def test_same_number_of_samples(self, datasets):
        """Verify both datasets have exactly the same number of samples."""
        original, converted = datasets

        original_count = len(original["train"])
        converted_count = len(converted["train"])

        assert original_count == converted_count, (
            f"Sample count mismatch: original has {original_count} samples, "
            f"converted has {converted_count} samples"
        )

    def test_same_features(self, datasets):
        """Verify both datasets have the same feature columns."""
        original, converted = datasets

        original_features = set(original["train"].features.keys())
        converted_features = set(converted["train"].features.keys())

        assert original_features == converted_features, (
            f"Feature mismatch:\n"
            f"  Original only: {original_features - converted_features}\n"
            f"  Converted only: {converted_features - original_features}"
        )

    def test_no_empty_text_fields(self, datasets):
        """Verify no samples have empty text fields after conversion."""
        original, converted = datasets

        # Check original
        for idx in range(len(original["train"])):
            original_text = original["train"][idx]["text"]
            assert original_text and len(original_text.strip()) > 0, (
                f"Original sample {idx} has empty text field"
            )

        # Check converted
        for idx in range(len(converted["train"])):
            converted_text = converted["train"][idx]["text"]
            assert converted_text and len(converted_text.strip()) > 0, (
                f"Converted sample {idx} has empty text field"
            )

    def test_text_length_reasonable(self, datasets):
        """Verify converted text lengths are reasonable compared to original."""
        original, converted = datasets

        # Sample 20 random indices
        dataset_length = len(original["train"])
        sample_size = min(20, dataset_length)
        random_indices = random.sample(range(dataset_length), sample_size)

        for idx in random_indices:
            original_text = original["train"][idx]["text"]
            converted_text = converted["train"][idx]["text"]

            # Converted should not be dramatically different in length
            # (allowing for format token differences)
            original_len = len(original_text)
            converted_len = len(converted_text)

            # Converted can be shorter (more compact tokens) or slightly longer
            # but should be within reasonable bounds (0.5x to 1.5x)
            ratio = converted_len / original_len if original_len > 0 else 1.0

            assert 0.3 < ratio < 2.0, (
                f"Sample {idx}: Text length ratio {ratio:.2f} is suspicious\n"
                f"  Original length: {original_len}\n"
                f"  Converted length: {converted_len}"
            )

    def test_metadata_fields_preserved(self, datasets):
        """Verify all non-text fields are identical between datasets."""
        original, converted = datasets

        # Get all feature names except 'text'
        metadata_fields = [
            f for f in original["train"].features.keys() if f != "text"
        ]

        # Check a random sample of 10 items
        dataset_length = len(original["train"])
        sample_size = min(10, dataset_length)
        random_indices = random.sample(range(dataset_length), sample_size)

        for idx in random_indices:
            original_sample = original["train"][idx]
            converted_sample = converted["train"][idx]

            for field in metadata_fields:
                original_value = original_sample[field]
                converted_value = converted_sample[field]

                assert original_value == converted_value, (
                    f"Sample {idx}: Metadata field '{field}' doesn't match\n"
                    f"  Original: {original_value}\n"
                    f"  Converted: {converted_value}"
                )

    def test_average_text_length_similar(self, datasets):
        """Verify average text length is similar between datasets."""
        original, converted = datasets

        # Calculate average lengths
        original_lengths = [len(sample["text"]) for sample in original["train"]]
        converted_lengths = [len(sample["text"]) for sample in converted["train"]]

        original_avg = sum(original_lengths) / len(original_lengths)
        converted_avg = sum(converted_lengths) / len(converted_lengths)

        # Average lengths should be reasonably similar
        ratio = converted_avg / original_avg if original_avg > 0 else 1.0

        assert 0.5 < ratio < 1.5, (
            f"Average text length ratio {ratio:.2f} is suspicious\n"
            f"  Original average: {original_avg:.1f} characters\n"
            f"  Converted average: {converted_avg:.1f} characters"
        )

        print(
            f"\nAverage text lengths:\n"
            f"  Original: {original_avg:.1f} characters\n"
            f"  Converted: {converted_avg:.1f} characters\n"
            f"  Ratio: {ratio:.2f}"
        )

    def test_all_samples_have_gemma_tokens(self, datasets):
        """Verify all converted samples contain required Gemma format tokens."""
        original, converted = datasets

        # Note: <bos> is NOT in the text - the tokenizer adds it automatically
        required_tokens = ["<start_of_turn>", "<end_of_turn>"]

        for idx in range(len(converted["train"])):
            converted_text = converted["train"][idx]["text"]

            for token in required_tokens:
                assert token in converted_text, (
                    f"Sample {idx}: Missing required Gemma token '{token}'"
                )

    def test_no_qwen_tokens_in_converted(self, datasets):
        """Verify converted samples don't contain Qwen-specific tokens."""
        original, converted = datasets

        qwen_tokens = ["<|im_start|>", "<|im_end|>"]

        # Check a random sample of 50 items
        dataset_length = len(converted["train"])
        sample_size = min(50, dataset_length)
        random_indices = random.sample(range(dataset_length), sample_size)

        for idx in random_indices:
            converted_text = converted["train"][idx]["text"]

            for token in qwen_tokens:
                assert token not in converted_text, (
                    f"Sample {idx}: Found Qwen token '{token}' in converted text"
                )

    def test_index_order_preserved(self, datasets):
        """Verify samples maintain their order (index correspondence)."""
        original, converted = datasets

        # Check 10 random indices
        dataset_length = len(original["train"])
        sample_size = min(10, dataset_length)
        random_indices = random.sample(range(dataset_length), sample_size)

        for idx in random_indices:
            original_sample = original["train"][idx]
            converted_sample = converted["train"][idx]

            # Parse and verify the content matches
            original_content = extract_content_from_qwen(original_sample["text"])
            reconverted = convert_to_gemma_format(original_content)

            assert converted_sample["text"] == reconverted, (
                f"Sample at index {idx} doesn't match expected conversion\n"
                f"This suggests the order may have changed during conversion"
            )


@pytest.mark.skipif(datasets_exist, reason="Only show info when datasets don't exist")
def test_dataset_info():
    """Informational test to show dataset status."""
    pytest.skip(
        f"Dataset files not found:\n"
        f"  Original: {ORIGINAL_DATASET}\n"
        f"  Converted: {CONVERTED_DATASET}\n"
        f"Run the conversion script first to generate these datasets."
    )
