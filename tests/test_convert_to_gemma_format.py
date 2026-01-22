"""
Tests for convert_to_gemma_format script.

Tests the conversion of Qwen-formatted training data to Gemma format,
including parsing and transformation functions.
"""

import sys
from pathlib import Path

# Add scripts directory to path to import the module
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from convert_to_gemma_format import parse_qwen_text, convert_to_gemma_format


class TestParseQwenText:
    """Tests for parse_qwen_text function."""

    def test_parse_complete_qwen_text(self):
        """Test parsing a complete Qwen-formatted text with all components."""
        qwen_text = """<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
What is 2+2?<|im_end|>
<|im_start|>think
Let me calculate this simple addition.
2 + 2 = 4<|im_start|>answer
The answer is 4.<|im_end|>"""

        result = parse_qwen_text(qwen_text)

        assert result['system'] == "You are a helpful assistant."
        assert result['user'] == "What is 2+2?"
        assert "Let me calculate this simple addition" in result['thinking']
        assert "2 + 2 = 4" in result['thinking']
        assert result['answer'] == "The answer is 4."

    def test_parse_without_system(self):
        """Test parsing Qwen text without system message."""
        qwen_text = """<|im_start|>user
Hello!<|im_end|>
<|im_start|>think
User is greeting me.<|im_start|>answer
Hi there!<|im_end|>"""

        result = parse_qwen_text(qwen_text)

        assert result['system'] == ""
        assert result['user'] == "Hello!"
        assert result['thinking'] == "User is greeting me."
        assert result['answer'] == "Hi there!"

    def test_parse_without_thinking(self):
        """Test parsing Qwen text without thinking section."""
        qwen_text = """<|im_start|>system
You are helpful.<|im_end|>
<|im_start|>user
Quick question<|im_end|>
<|im_start|>answer
Quick answer<|im_end|>"""

        result = parse_qwen_text(qwen_text)

        assert result['system'] == "You are helpful."
        assert result['user'] == "Quick question"
        assert result['thinking'] == ""
        assert result['answer'] == "Quick answer"

    def test_parse_multiline_components(self):
        """Test parsing with multiline content in each component."""
        qwen_text = """<|im_start|>system
You are a helpful assistant.
You should be polite and accurate.<|im_end|>
<|im_start|>user
Line 1 of question
Line 2 of question
Line 3 of question<|im_end|>
<|im_start|>think
Step 1: analyze
Step 2: process
Step 3: conclude<|im_start|>answer
Part 1 of answer
Part 2 of answer<|im_end|>"""

        result = parse_qwen_text(qwen_text)

        assert "You are a helpful assistant" in result['system']
        assert "You should be polite and accurate" in result['system']
        assert "Line 1 of question" in result['user']
        assert "Line 3 of question" in result['user']
        assert "Step 1: analyze" in result['thinking']
        assert "Step 3: conclude" in result['thinking']
        assert "Part 1 of answer" in result['answer']
        assert "Part 2 of answer" in result['answer']

    def test_parse_empty_text(self):
        """Test parsing empty or minimal text."""
        result = parse_qwen_text("")

        assert result['system'] == ""
        assert result['user'] == ""
        assert result['thinking'] == ""
        assert result['answer'] == ""

    def test_parse_only_user_message(self):
        """Test parsing with only user message."""
        qwen_text = "<|im_start|>user\nJust a user message<|im_end|>"

        result = parse_qwen_text(qwen_text)

        assert result['system'] == ""
        assert result['user'] == "Just a user message"
        assert result['thinking'] == ""
        assert result['answer'] == ""


class TestConvertToGemmaFormat:
    """Tests for convert_to_gemma_format function."""

    def test_convert_complete_components(self):
        """Test conversion with all components present."""
        components = {
            'system': 'You are helpful.',
            'user': 'What is AI?',
            'thinking': 'AI stands for Artificial Intelligence.',
            'answer': 'AI is artificial intelligence.'
        }

        result = convert_to_gemma_format(components)

        assert result.startswith("<bos><start_of_turn>user\n")
        assert "You are helpful." in result
        assert "What is AI?" in result
        assert "<end_of_turn>\n<start_of_turn>model\n" in result
        assert "[Thinking: AI stands for Artificial Intelligence.]" in result
        assert "[Answer: AI is artificial intelligence.]" in result
        assert result.endswith("<end_of_turn>")

    def test_convert_without_system(self):
        """Test conversion without system message."""
        components = {
            'system': '',
            'user': 'Hello',
            'thinking': 'Greeting detected',
            'answer': 'Hi!'
        }

        result = convert_to_gemma_format(components)

        assert "<bos><start_of_turn>user\n" in result
        assert "Hello<end_of_turn>" in result
        assert "[Thinking: Greeting detected]" in result
        assert "[Answer: Hi!]" in result
        # System message should not appear
        assert result.count('\n\n') >= 1  # At least thinking/answer separation

    def test_convert_without_thinking(self):
        """Test conversion without thinking section."""
        components = {
            'system': 'Be brief.',
            'user': 'Hi',
            'thinking': '',
            'answer': 'Hello!'
        }

        result = convert_to_gemma_format(components)

        assert "Be brief." in result
        assert "Hi<end_of_turn>" in result
        assert "[Thinking:" not in result
        assert "[Answer: Hello!]" in result

    def test_convert_system_prepended_to_user(self):
        """Test that system message is correctly prepended to user message."""
        components = {
            'system': 'System instruction',
            'user': 'User query',
            'thinking': 'Think',
            'answer': 'Ans'
        }

        result = convert_to_gemma_format(components)

        # Extract user turn
        user_section = result.split("<end_of_turn>")[0]
        user_content = user_section.split("<start_of_turn>user\n")[1]

        assert "System instruction" in user_content
        assert "User query" in user_content
        # System should come before user
        assert user_content.index("System instruction") < user_content.index("User query")

    def test_convert_empty_components(self):
        """Test conversion with all empty components."""
        components = {
            'system': '',
            'user': '',
            'thinking': '',
            'answer': ''
        }

        result = convert_to_gemma_format(components)

        # Should still have proper structure
        assert result.startswith("<bos><start_of_turn>user\n")
        assert "<end_of_turn>" in result
        assert "<start_of_turn>model\n" in result
        assert result.endswith("<end_of_turn>")

    def test_convert_preserves_newlines(self):
        """Test that multiline content is preserved."""
        components = {
            'system': 'Line 1\nLine 2',
            'user': 'Question\nwith\nmultiple\nlines',
            'thinking': 'Step 1\nStep 2\nStep 3',
            'answer': 'Answer\nwith\nlines'
        }

        result = convert_to_gemma_format(components)

        assert "Line 1\nLine 2" in result
        assert "Question\nwith\nmultiple\nlines" in result
        assert "Step 1\nStep 2\nStep 3" in result
        assert "Answer\nwith\nlines" in result


class TestEndToEndConversion:
    """End-to-end integration tests."""

    def test_full_conversion_pipeline(self):
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

        # Verify parsing
        assert components['system'] == "You are a math tutor."
        assert components['user'] == "What is 5 * 6?"
        assert components['thinking'] == "5 times 6 equals 30."
        assert components['answer'] == "5 * 6 = 30"

        # Convert
        gemma_text = convert_to_gemma_format(components)

        # Verify conversion
        assert gemma_text.startswith("<bos><start_of_turn>user\n")
        assert "You are a math tutor." in gemma_text
        assert "What is 5 * 6?" in gemma_text
        assert "[Thinking: 5 times 6 equals 30.]" in gemma_text
        assert "[Answer: 5 * 6 = 30]" in gemma_text
        assert gemma_text.endswith("<end_of_turn>")

    def test_conversion_minimal_input(self):
        """Test pipeline with minimal input."""
        qwen_text = """<|im_start|>user
Hi<|im_end|>
<|im_start|>answer
Hello<|im_end|>"""

        components = parse_qwen_text(qwen_text)
        gemma_text = convert_to_gemma_format(components)

        assert components['user'] == "Hi"
        assert components['answer'] == "Hello"
        assert "Hi<end_of_turn>" in gemma_text
        assert "[Answer: Hello]" in gemma_text

    def test_conversion_with_special_characters(self):
        """Test handling of special characters and symbols."""
        qwen_text = """<|im_start|>user
Calculate: 2 < 5 & 3 > 1<|im_end|>
<|im_start|>answer
True && True = True<|im_end|>"""

        components = parse_qwen_text(qwen_text)
        gemma_text = convert_to_gemma_format(components)

        assert "2 < 5 & 3 > 1" in gemma_text
        assert "True && True = True" in gemma_text


class TestContentPreservation:
    """Tests to verify that actual content is preserved during conversion."""

    def test_exact_content_preservation(self):
        """
        Verify that the exact content (excluding formatting tokens) is preserved.

        This test ensures that system, user, thinking, and answer content
        appears exactly as-is in the converted output.
        """
        # Define exact content we expect to preserve
        system_content = "You are a helpful AI assistant specialized in mathematics."
        user_content = "Can you help me solve this equation: 3x + 7 = 22?"
        thinking_content = "Let me solve this step by step:\n1. Subtract 7 from both sides: 3x = 15\n2. Divide both sides by 3: x = 5"
        answer_content = "The solution is x = 5.\n\nTo verify: 3(5) + 7 = 15 + 7 = 22 ✓"

        # Create Qwen format with this content
        qwen_text = f"""<|im_start|>system
{system_content}<|im_end|>
<|im_start|>user
{user_content}<|im_end|>
<|im_start|>think
{thinking_content}<|im_start|>answer
{answer_content}<|im_end|>"""

        # Parse and convert
        components = parse_qwen_text(qwen_text)
        gemma_text = convert_to_gemma_format(components)

        # Verify exact content is preserved in parsed components
        assert components['system'] == system_content
        assert components['user'] == user_content
        assert components['thinking'] == thinking_content
        assert components['answer'] == answer_content

        # Verify exact content appears in Gemma output
        assert system_content in gemma_text
        assert user_content in gemma_text
        assert thinking_content in gemma_text
        assert answer_content in gemma_text

    def test_no_content_modification(self):
        """
        Verify that content with various formatting is not modified.

        Tests that code blocks, special characters, and formatting within
        content are preserved exactly.
        """
        # Content with code, special chars, and formatting
        system_content = "System: Use markdown formatting in responses."
        user_content = """Write a function to check if a string is a palindrome.
Include these test cases:
- "racecar" → True
- "hello" → False"""

        thinking_content = """I'll write a Python function:
```python
def is_palindrome(s):
    return s == s[::-1]
```
This uses string slicing to reverse & compare."""

        answer_content = """Here's the solution:

```python
def is_palindrome(text):
    # Remove spaces and convert to lowercase
    text = text.replace(" ", "").lower()
    return text == text[::-1]

# Test cases
print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False
```

The function returns `True` if the string reads the same forwards and backwards."""

        # Create and convert
        qwen_text = f"""<|im_start|>system
{system_content}<|im_end|>
<|im_start|>user
{user_content}<|im_end|>
<|im_start|>think
{thinking_content}<|im_start|>answer
{answer_content}<|im_end|>"""

        components = parse_qwen_text(qwen_text)
        gemma_text = convert_to_gemma_format(components)

        # Verify exact preservation including code blocks and special chars
        assert components['system'] == system_content
        assert components['user'] == user_content
        assert components['thinking'] == thinking_content
        assert components['answer'] == answer_content

        # Verify in final output
        assert "```python" in gemma_text
        assert "def is_palindrome" in gemma_text
        assert "s[::-1]" in gemma_text
        assert "# Test cases" in gemma_text

    def test_content_length_preservation(self):
        """
        Verify that no content is lost - total content length is preserved.

        The Gemma format should contain all the original content plus
        only the formatting tokens.
        """
        system_content = "Be concise."
        user_content = "What is Python?"
        thinking_content = "Python is a programming language."
        answer_content = "Python is a high-level programming language."

        qwen_text = f"""<|im_start|>system
{system_content}<|im_end|>
<|im_start|>user
{user_content}<|im_end|>
<|im_start|>think
{thinking_content}<|im_start|>answer
{answer_content}<|im_end|>"""

        components = parse_qwen_text(qwen_text)
        gemma_text = convert_to_gemma_format(components)

        # Calculate total content length
        total_content_length = (
            len(system_content) +
            len(user_content) +
            len(thinking_content) +
            len(answer_content)
        )

        # Gemma text should be longer (due to format tokens) but contain all content
        assert len(gemma_text) > total_content_length

        # Every character from original content should be findable in output
        for content in [system_content, user_content, thinking_content, answer_content]:
            if content:  # Skip empty strings
                assert content in gemma_text

    def test_unicode_and_emoji_preservation(self):
        """Verify that unicode characters and emojis are preserved exactly."""
        system_content = "Système de réponse multilingue 🌍"
        user_content = "Quelle est la température en °C? 🌡️"
        thinking_content = "La température moyenne est d'environ 20°C ≈ 68°F"
        answer_content = "Il fait environ 20°C (soixante-huit degrés Fahrenheit) ✓"

        qwen_text = f"""<|im_start|>system
{system_content}<|im_end|>
<|im_start|>user
{user_content}<|im_end|>
<|im_start|>think
{thinking_content}<|im_start|>answer
{answer_content}<|im_end|>"""

        components = parse_qwen_text(qwen_text)
        gemma_text = convert_to_gemma_format(components)

        # Verify unicode and emojis are preserved
        assert "🌍" in gemma_text
        assert "🌡️" in gemma_text
        assert "°C" in gemma_text
        assert "≈" in gemma_text
        assert "✓" in gemma_text
        assert "Système" in gemma_text
        assert "température" in gemma_text

    def test_whitespace_preservation(self):
        """Verify that important whitespace (newlines, indentation) is preserved."""
        thinking_content = """Step 1: Initialize variables
    x = 0
    y = 0

Step 2: Process data
    for item in items:
        process(item)

Step 3: Return result"""

        components = {
            'system': '',
            'user': 'Test whitespace',
            'thinking': thinking_content,
            'answer': 'Done'
        }

        gemma_text = convert_to_gemma_format(components)

        # Verify indentation and newlines are preserved
        assert "    x = 0" in gemma_text
        assert "    y = 0" in gemma_text
        assert "    for item in items:" in gemma_text
        assert "        process(item)" in gemma_text
        assert "Step 1: Initialize variables" in gemma_text
        assert "Step 3: Return result" in gemma_text

    def test_content_order_preservation(self):
        """Verify that content appears in the correct order in output."""
        system_content = "SYSTEM_MARKER"
        user_content = "USER_MARKER"
        thinking_content = "THINKING_MARKER"
        answer_content = "ANSWER_MARKER"

        components = {
            'system': system_content,
            'user': user_content,
            'thinking': thinking_content,
            'answer': answer_content
        }

        gemma_text = convert_to_gemma_format(components)

        # Find positions of markers
        system_pos = gemma_text.index("SYSTEM_MARKER")
        user_pos = gemma_text.index("USER_MARKER")
        thinking_pos = gemma_text.index("THINKING_MARKER")
        answer_pos = gemma_text.index("ANSWER_MARKER")

        # Verify order: system before user (in user turn), then thinking before answer (in model turn)
        assert system_pos < user_pos, "System should appear before user"
        assert user_pos < thinking_pos, "User should appear before thinking"
        assert thinking_pos < answer_pos, "Thinking should appear before answer"
