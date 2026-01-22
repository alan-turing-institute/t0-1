# Tests

This directory contains tests for the t0 project.

## Running Tests

To run all tests using `uv`:

```bash
uv run pytest tests/
```

To run tests with verbose output:

```bash
uv run pytest tests/ -v
```

To run a specific test file:

```bash
uv run pytest tests/test_convert_to_gemma_format.py -v
```

## Test Coverage

### test_convert_to_gemma_format.py

Unit tests for the `convert_to_gemma_format.py` script that converts Qwen-formatted training data to Gemma format.

**Test Classes:**

1. **TestParseQwenText** - Tests for the `parse_qwen_text()` function (6 tests)
   - Complete Qwen text parsing with all components
   - Parsing without system messages
   - Parsing without thinking sections
   - Multiline content handling
   - Empty/minimal input handling
   - User-only messages

2. **TestConvertToGemmaFormat** - Tests for the `convert_to_gemma_format()` function (6 tests)
   - Complete component conversion
   - Conversion without system messages
   - Conversion without thinking sections
   - System message prepending to user messages
   - Empty component handling
   - Multiline content preservation

3. **TestEndToEndConversion** - Integration tests for the full pipeline (3 tests)
   - Full Qwen to Gemma conversion pipeline
   - Minimal input conversion
   - Special character handling

4. **TestContentPreservation** - Tests verifying content is preserved exactly (6 tests)
   - Exact content preservation across all components
   - Content with code blocks and special characters
   - Content length preservation
   - Unicode and emoji preservation
   - Whitespace and indentation preservation
   - Content order verification

### test_dataset_conversion.py

Integration tests that verify conversion correctness on actual dataset files. These tests check that random elements from `data/reasoning_traces/2k-deepseek-traces-k5_qwen_summarised_data` have identical content (excluding boilerplate tokens) in the converted `data/reasoning_traces/2k-deepseek-traces-k5_qwen_summarised_data_gemma` dataset.

**Test Classes:**

1. **TestDatasetConversion** - Content preservation integration tests (6 tests)
   - Dataset length matching verification
   - Random sample content preservation
   - Multiple random samples (tests 10 samples)
   - First sample content verification
   - Gemma format structure validation (checks 50 samples)
   - Content duplication detection

2. **TestDatasetStructure** - General dataset structure and properties (9 tests)
   - Same number of samples verification
   - Same feature columns verification
   - No empty text fields check
   - Text length reasonableness (checks ratio between 0.3x-2.0x)
   - Metadata fields preserved (non-text fields identical)
   - Average text length similarity (within 0.5x-1.5x ratio)
   - All samples have required Gemma tokens
   - No Qwen tokens in converted dataset
   - Index order preservation verification

**Note:** These tests automatically skip if the dataset files don't exist. Run the conversion script first to generate the datasets.

## Adding New Tests

When adding new test files:

1. Create test files with the prefix `test_`
2. Use descriptive class names with the prefix `Test`
3. Use descriptive test function names with the prefix `test_`
4. Group related tests into classes
5. Add docstrings to explain what each test validates
