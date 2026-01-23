# Tests

Tests for the Qwen to Gemma format conversion and SFT training setup.

## Running Tests

```bash
uv run --extra dev pytest tests/ -v
```

## Test Files

### test_convert_to_gemma_format.py

Tests the conversion of Qwen-formatted training data to Gemma format.

- `test_parse_qwen_text` - Verifies parsing of Qwen format extracts system, user, thinking, and answer components
- `test_convert_to_gemma_format` - Verifies conversion produces correct Gemma format structure
- `test_full_pipeline` - End-to-end test: parse Qwen text → convert → verify Gemma output
- `test_real_data_conversion` - Sanity check on real dataset samples (skips if datasets don't exist)

### test_sft.py

Tests template consistency between conversion script and SFT training.

- `test_response_template_in_converted_output` - Verifies `<start_of_turn>model\n` appears in converted text
- `test_instruction_template_in_converted_output` - Verifies `<start_of_turn>user` appears in converted text
- `test_no_bos_token_in_converted_text` - Verifies no `<bos>` in text (tokenizer adds it automatically)
- `test_collator_masks_instruction_tokens` - Verifies DataCollator correctly masks instruction tokens (requires `trl`)
