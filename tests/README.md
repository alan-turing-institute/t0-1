# Tests

Tests for the Qwen to Gemma format conversion and SFT training setup.

## Running Tests

```bash
uv sync --extra dev
uv run pytest
```

## Test Files

### test_convert_to_gemma_format.py

Tests the conversion of Qwen-formatted training data to Gemma format.

- `test_parse_qwen_text` - Verifies parsing of Qwen format extracts system, user, thinking, and answer components
- `test_convert_to_gemma_format` - Verifies conversion produces correct Gemma format structure
- `test_full_pipeline` - End-to-end test: parse Qwen text → convert → verify Gemma output
- `test_real_data_conversion` - Sanity check on real dataset samples (skips if datasets don't exist)

### test_sft.py

Tests that DataCollatorForCompletionOnlyLM works correctly with Gemma format.

- `test_collator_masks_instruction_tokens` - Verifies DataCollator correctly masks instruction tokens (requires `trl`)
