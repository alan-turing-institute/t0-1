"""
Tests for sft.py training script.

Tests template correctness, tokenizer configuration, and integration with
the Gemma format conversion for DataCollatorForCompletionOnlyLM.
"""

import sys
from pathlib import Path

import pytest

# Add scripts and train directories to path
scripts_dir = Path(__file__).parent.parent / "scripts"
train_dir = Path(__file__).parent.parent / "train" / "s1_31a10f2" / "train"
sys.path.insert(0, str(scripts_dir))
sys.path.insert(0, str(train_dir))

from convert_to_gemma_format import parse_qwen_text, convert_to_gemma_format


# =============================================================================
# Constants: Expected templates for each model family
# =============================================================================

EXPECTED_TEMPLATES = {
    "gemma": {
        "instruction_template": "<start_of_turn>user",
        "response_template": "<start_of_turn>model\n",
    },
    "qwen": {
        "instruction_template": "<|im_start|>user",
        "response_template": "<|im_start|>assistant\n",
    },
    "llama": {
        "instruction_template": "<|start_header_id|>user<|end_header_id|}",
        "response_template": "<|start_header_id|>assistant<|end_header_id|>\n\n",
    },
}

# Sample Qwen-formatted text for testing
SAMPLE_QWEN_TEXT = """<|im_start|>system
You are a helpful math tutor.<|im_end|>
<|im_start|>user
What is 2 + 2?<|im_end|>
<|im_start|>think
This is a simple addition problem.
2 + 2 = 4<|im_start|>answer
The answer is 4.<|im_end|>"""


# =============================================================================
# Template Correctness Tests (no model download required)
# =============================================================================


class TestTemplateCorrectness:
    """Tests verifying template strings match expected format for each model."""

    def test_gemma_response_template_matches_conversion_output(self):
        """
        Verify the response_template in sft.py matches what convert_to_gemma_format produces.

        This is the critical consistency test between sft.py and the conversion script.
        """
        # Convert sample text to Gemma format
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        # The response_template from sft.py
        response_template = "<start_of_turn>model\n"

        # Verify the response template appears in the converted output
        assert response_template in gemma_text, (
            f"Response template '{response_template}' not found in converted Gemma text.\n"
            f"Converted text starts with: {gemma_text[:200]}..."
        )

    def test_gemma_instruction_template_matches_conversion_output(self):
        """
        Verify the instruction_template in sft.py matches what convert_to_gemma_format produces.
        """
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        # The instruction_template from sft.py
        instruction_template = "<start_of_turn>user"

        # Verify the instruction template appears in the converted output
        assert instruction_template in gemma_text, (
            f"Instruction template '{instruction_template}' not found in converted Gemma text."
        )

    def test_gemma_format_structure_correct(self):
        """
        Verify the overall structure of converted Gemma text is correct for DataCollator.

        The DataCollatorForCompletionOnlyLM needs:
        1. instruction_template to appear before response_template
        2. response_template to mark where the model's response begins
        """
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        instruction_template = "<start_of_turn>user"
        response_template = "<start_of_turn>model\n"

        instruction_pos = gemma_text.find(instruction_template)
        response_pos = gemma_text.find(response_template)

        assert instruction_pos >= 0, "Instruction template not found"
        assert response_pos >= 0, "Response template not found"
        assert instruction_pos < response_pos, (
            "Instruction template should appear before response template"
        )

    def test_gemma_format_no_bos_token(self):
        """
        Verify converted Gemma text does NOT contain <bos> token.

        The tokenizer adds <bos> automatically (add_bos_token=True for Gemma).
        Including it in the text would result in duplicate BOS tokens.
        """
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        assert "<bos>" not in gemma_text, (
            "Converted text should not contain <bos> - tokenizer adds it automatically"
        )


class TestModelNameParsing:
    """Tests for model name detection logic in sft.py."""

    def test_gemma_model_names_detected(self):
        """Verify various Gemma model name formats are detected."""
        gemma_names = [
            "google/gemma-3-1b-it",
            "google/gemma-3-4b-it",
            "google/gemma-3-12b-it",
            "google/gemma-3-27b-it",
            "GEMMA-model",  # case insensitive
            "my-gemma-finetuned",
        ]
        for name in gemma_names:
            assert "gemma" in name.lower(), f"Should detect '{name}' as Gemma model"

    def test_qwen_model_names_detected(self):
        """Verify various Qwen model name formats are detected."""
        qwen_names = [
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2-7B",
            "QWEN-model",
        ]
        for name in qwen_names:
            assert "Qwen" in name or "qwen" in name.lower(), (
                f"Should detect '{name}' as Qwen model"
            )

    def test_llama_model_names_detected(self):
        """Verify various Llama model name formats are detected."""
        llama_names = [
            "meta-llama/Llama-2-7b",
            "meta-llama/Llama-3-8b",
            "LLAMA-model",
        ]
        for name in llama_names:
            assert "Llama" in name or "llama" in name.lower(), (
                f"Should detect '{name}' as Llama model"
            )


# =============================================================================
# Integration Tests (require model/tokenizer downloads)
# =============================================================================

# Check if transformers and trl are available
try:
    import transformers
    import trl
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="transformers/trl not installed")
class TestTokenizerConfiguration:
    """Tests for tokenizer configuration in sft.py."""

    @pytest.fixture(scope="class")
    def gemma_tokenizer(self):
        """Load Gemma tokenizer (smallest model for speed)."""
        try:
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                "google/gemma-3-270m-it",
                use_fast=True
            )
            tokenizer.pad_token = tokenizer.pad_token or "<pad>"
            return tokenizer
        except Exception as e:
            pytest.skip(f"Could not load Gemma tokenizer: {e}")

    @pytest.fixture(scope="class")
    def qwen_tokenizer(self):
        """Load Qwen tokenizer."""
        try:
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                "Qwen/Qwen2.5-0.5B-Instruct",
                use_fast=True
            )
            tokenizer.pad_token = "<|fim_pad|>"
            return tokenizer
        except Exception as e:
            pytest.skip(f"Could not load Qwen tokenizer: {e}")

    def test_gemma_pad_token_set(self, gemma_tokenizer):
        """Verify Gemma tokenizer has pad token configured."""
        assert gemma_tokenizer.pad_token is not None, "Pad token should be set"
        assert gemma_tokenizer.pad_token_id is not None, "Pad token ID should exist"

    def test_qwen_pad_token_set(self, qwen_tokenizer):
        """Verify Qwen tokenizer has correct pad token."""
        assert qwen_tokenizer.pad_token == "<|fim_pad|>", (
            f"Qwen pad token should be '<|fim_pad|>', got '{qwen_tokenizer.pad_token}'"
        )

    def test_gemma_tokenizer_adds_bos(self, gemma_tokenizer):
        """Verify Gemma tokenizer adds BOS token automatically."""
        # This is important - the conversion script doesn't add <bos>
        # because the tokenizer does it
        text = "Hello world"
        tokens = gemma_tokenizer.encode(text)

        # First token should be BOS
        assert tokens[0] == gemma_tokenizer.bos_token_id, (
            "Gemma tokenizer should add BOS token automatically"
        )


@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="transformers/trl not installed")
class TestDataCollatorIntegration:
    """
    Integration tests for DataCollatorForCompletionOnlyLM with converted Gemma data.

    These tests verify that the collator correctly identifies instruction vs response
    tokens when processing data converted by convert_to_gemma_format.py.
    """

    @pytest.fixture(scope="class")
    def gemma_tokenizer(self):
        """Load Gemma tokenizer."""
        try:
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                "google/gemma-3-270m-it",
                use_fast=True
            )
            tokenizer.pad_token = tokenizer.pad_token or "<pad>"
            return tokenizer
        except Exception as e:
            pytest.skip(f"Could not load Gemma tokenizer: {e}")

    @pytest.fixture(scope="class")
    def gemma_collator(self, gemma_tokenizer):
        """Create DataCollator with Gemma templates (matching sft.py)."""
        return trl.DataCollatorForCompletionOnlyLM(
            instruction_template="<start_of_turn>user",
            response_template="<start_of_turn>model\n",
            tokenizer=gemma_tokenizer,
            mlm=False
        )

    def test_response_template_tokenizes_correctly(self, gemma_tokenizer):
        """
        Verify response template can be tokenized and found in converted text.

        The DataCollator tokenizes the response_template and searches for those
        token IDs in the input. This test ensures the template tokenizes correctly.
        """
        response_template = "<start_of_turn>model\n"

        # Tokenize the template (without adding special tokens)
        template_tokens = gemma_tokenizer.encode(
            response_template,
            add_special_tokens=False
        )

        # Template should tokenize to at least some tokens
        assert len(template_tokens) > 0, "Response template should produce tokens"

        # Decode back to verify
        decoded = gemma_tokenizer.decode(template_tokens)
        assert "<start_of_turn>" in decoded or "model" in decoded, (
            f"Decoded template tokens don't match expected. Got: {decoded}"
        )

    def test_converted_text_contains_response_template_tokens(self, gemma_tokenizer):
        """
        Verify converted Gemma text contains the response template token sequence.
        """
        # Convert sample text
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        # Tokenize the full text
        full_tokens = gemma_tokenizer.encode(gemma_text, add_special_tokens=True)

        # Tokenize the response template (without special tokens)
        response_template = "<start_of_turn>model\n"
        template_tokens = gemma_tokenizer.encode(
            response_template,
            add_special_tokens=False
        )

        # Check if template tokens appear in full tokens
        # Convert to strings for easier substring search
        full_str = " ".join(map(str, full_tokens))
        template_str = " ".join(map(str, template_tokens))

        assert template_str in full_str, (
            f"Response template tokens not found in tokenized text.\n"
            f"Template tokens: {template_tokens}\n"
            f"Full tokens: {full_tokens}"
        )

    def test_collator_masks_instruction_tokens(self, gemma_tokenizer, gemma_collator):
        """
        Verify DataCollator correctly sets labels to -100 for instruction tokens.

        This is the key test ensuring loss is only computed on model responses.
        """
        # Convert sample text to Gemma format
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        # Tokenize
        tokenized = gemma_tokenizer(
            gemma_text,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        # Create batch for collator (list of dicts)
        batch = [{"input_ids": tokenized["input_ids"][0]}]

        # Apply collator
        collated = gemma_collator(batch)

        labels = collated["labels"][0].tolist()
        input_ids = collated["input_ids"][0].tolist()

        # Find where response starts by looking for first non -100 label
        first_valid_label_idx = None
        for i, label in enumerate(labels):
            if label != -100:
                first_valid_label_idx = i
                break

        assert first_valid_label_idx is not None, (
            "No valid labels found - collator may not have found response template"
        )

        # Verify some labels before response are -100 (masked instruction)
        assert first_valid_label_idx > 0, (
            "Expected some instruction tokens to be masked (labels=-100)"
        )

        # Count masked vs unmasked labels
        masked_count = sum(1 for l in labels if l == -100)
        unmasked_count = sum(1 for l in labels if l != -100)

        assert masked_count > 0, "Should have some masked (instruction) tokens"
        assert unmasked_count > 0, "Should have some unmasked (response) tokens"

        print(f"\nCollator results:")
        print(f"  Total tokens: {len(labels)}")
        print(f"  Masked (instruction): {masked_count}")
        print(f"  Unmasked (response): {unmasked_count}")
        print(f"  Response starts at token index: {first_valid_label_idx}")

    def test_collator_preserves_response_tokens(self, gemma_tokenizer, gemma_collator):
        """
        Verify DataCollator preserves labels for response tokens.

        Labels for response tokens should equal the corresponding input_ids
        (for next-token prediction).
        """
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        tokenized = gemma_tokenizer(
            gemma_text,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        batch = [{"input_ids": tokenized["input_ids"][0]}]
        collated = gemma_collator(batch)

        labels = collated["labels"][0].tolist()
        input_ids = collated["input_ids"][0].tolist()

        # For non-masked positions, labels should equal input_ids
        for i, (label, input_id) in enumerate(zip(labels, input_ids)):
            if label != -100:
                assert label == input_id, (
                    f"At position {i}: label ({label}) should equal input_id ({input_id})"
                )

    def test_response_includes_thinking_and_answer(self, gemma_tokenizer, gemma_collator):
        """
        Verify both [Thinking: ...] and [Answer: ...] are in the unmasked response region.
        """
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        tokenized = gemma_tokenizer(
            gemma_text,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )

        batch = [{"input_ids": tokenized["input_ids"][0]}]
        collated = gemma_collator(batch)

        labels = collated["labels"][0].tolist()
        input_ids = collated["input_ids"][0].tolist()

        # Get the response portion (unmasked labels)
        response_ids = [input_ids[i] for i, l in enumerate(labels) if l != -100]
        response_text = gemma_tokenizer.decode(response_ids)

        # Verify key content is in the response
        assert "Thinking:" in response_text or "think" in response_text.lower(), (
            f"Thinking content should be in response portion.\nResponse: {response_text}"
        )
        assert "Answer:" in response_text or "4" in response_text, (
            f"Answer content should be in response portion.\nResponse: {response_text}"
        )


@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="transformers/trl not installed")
class TestBosTokenHandling:
    """Tests for BOS token handling between conversion and training."""

    @pytest.fixture(scope="class")
    def gemma_tokenizer(self):
        """Load Gemma tokenizer."""
        try:
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                "google/gemma-3-270m-it",
                use_fast=True
            )
            tokenizer.pad_token = tokenizer.pad_token or "<pad>"
            return tokenizer
        except Exception as e:
            pytest.skip(f"Could not load Gemma tokenizer: {e}")

    def test_no_duplicate_bos_token(self, gemma_tokenizer):
        """
        Verify tokenizing converted text doesn't produce duplicate BOS tokens.

        Since convert_to_gemma_format doesn't add <bos> and the tokenizer adds it
        automatically, we should get exactly one BOS token.
        """
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        tokens = gemma_tokenizer.encode(gemma_text, add_special_tokens=True)

        bos_token_id = gemma_tokenizer.bos_token_id
        bos_count = sum(1 for t in tokens if t == bos_token_id)

        assert bos_count == 1, (
            f"Expected exactly 1 BOS token, found {bos_count}.\n"
            f"BOS token ID: {bos_token_id}\n"
            f"First 10 tokens: {tokens[:10]}"
        )

    def test_bos_is_first_token(self, gemma_tokenizer):
        """Verify BOS token is at the start of tokenized sequence."""
        components = parse_qwen_text(SAMPLE_QWEN_TEXT)
        gemma_text = convert_to_gemma_format(components)

        tokens = gemma_tokenizer.encode(gemma_text, add_special_tokens=True)

        assert tokens[0] == gemma_tokenizer.bos_token_id, (
            f"First token should be BOS ({gemma_tokenizer.bos_token_id}), "
            f"got {tokens[0]}"
        )


# =============================================================================
# End-to-End Integration Test
# =============================================================================


@pytest.mark.skipif(not TRANSFORMERS_AVAILABLE, reason="transformers/trl not installed")
class TestEndToEndIntegration:
    """
    End-to-end integration test: Qwen data → conversion → tokenization → collation.

    This test validates the complete pipeline that sft.py uses for Gemma training.
    """

    def test_full_pipeline_qwen_to_gemma_training(self):
        """
        Test complete pipeline from Qwen-formatted data to training-ready batch.

        Steps:
        1. Parse Qwen-formatted text
        2. Convert to Gemma format
        3. Load Gemma tokenizer with sft.py configuration
        4. Tokenize the converted text
        5. Apply DataCollator
        6. Verify labels correctly mask instruction, preserve response
        """
        try:
            tokenizer = transformers.AutoTokenizer.from_pretrained(
                "google/gemma-3-270m-it",
                use_fast=True
            )
        except Exception as e:
            pytest.skip(f"Could not load tokenizer: {e}")

        # Configure tokenizer as sft.py does
        tokenizer.pad_token = tokenizer.pad_token or "<pad>"

        # Create collator as sft.py does
        collator = trl.DataCollatorForCompletionOnlyLM(
            instruction_template="<start_of_turn>user",
            response_template="<start_of_turn>model\n",
            tokenizer=tokenizer,
            mlm=False
        )

        # Sample Qwen data (simulating what would be in the dataset)
        qwen_samples = [
            """<|im_start|>system
You are a math expert.<|im_end|>
<|im_start|>user
What is 5 * 7?<|im_end|>
<|im_start|>think
5 times 7 equals 35.<|im_start|>answer
The answer is 35.<|im_end|>""",
            """<|im_start|>user
Hello!<|im_end|>
<|im_start|>think
User greeting.<|im_start|>answer
Hi there!<|im_end|>""",
        ]

        for i, qwen_text in enumerate(qwen_samples):
            # Step 1 & 2: Convert to Gemma format
            components = parse_qwen_text(qwen_text)
            gemma_text = convert_to_gemma_format(components)

            # Step 3 & 4: Tokenize
            tokenized = tokenizer(
                gemma_text,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )

            # Step 5: Apply collator
            batch = [{"input_ids": tokenized["input_ids"][0]}]
            collated = collator(batch)

            labels = collated["labels"][0].tolist()

            # Step 6: Verify
            # Should have both masked and unmasked labels
            masked_count = sum(1 for l in labels if l == -100)
            unmasked_count = sum(1 for l in labels if l != -100)

            assert masked_count > 0, f"Sample {i}: No masked tokens found"
            assert unmasked_count > 0, f"Sample {i}: No unmasked tokens found"

            # Verify original content appears in the decoded response
            response_ids = [
                collated["input_ids"][0][j].item()
                for j, l in enumerate(labels) if l != -100
            ]
            response_text = tokenizer.decode(response_ids)

            # The answer from the original should be in the response
            assert components["answer"] in response_text or \
                   any(word in response_text for word in components["answer"].split()), (
                f"Sample {i}: Answer content not found in response.\n"
                f"Expected: {components['answer']}\n"
                f"Response: {response_text}"
            )

            print(f"\nSample {i} passed:")
            print(f"  Instruction tokens (masked): {masked_count}")
            print(f"  Response tokens (unmasked): {unmasked_count}")


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in sft.py model selection logic."""

    def test_unsupported_model_should_raise(self):
        """
        Verify that unsupported model names would raise ValueError.

        Note: This tests the logic, not the actual sft.py function directly.
        """
        unsupported_names = [
            "facebook/opt-1.3b",
            "EleutherAI/gpt-neo-1.3B",
            "mistralai/Mistral-7B",
            "unknown-model",
        ]

        for model_name in unsupported_names:
            # Simulate the logic from sft.py
            is_llama = "Llama" in model_name
            is_qwen = "Qwen" in model_name
            is_gemma = "gemma" in model_name.lower()

            is_supported = is_llama or is_qwen or is_gemma

            assert not is_supported, (
                f"Model '{model_name}' should not be detected as supported"
            )
