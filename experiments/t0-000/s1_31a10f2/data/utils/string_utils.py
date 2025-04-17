def extract_content(input_string, start_token, end_token=None):
    start_index = input_string.find(start_token) + len(start_token)
    if end_token is None: return input_string[start_index:].strip()
    end_index = input_string.find(end_token)
    # Return None if neither token is found
    if start_index == -1 or end_index == -1: return None
    return input_string[start_index:end_index].strip()

def remove_special_tokens(input_string):
    """
    Remove the special tokens from the input string.
    """
    if input_string is None: return ""
    special_tokens = [
        '<|reserved_special_token_0|>',
        '<|reserved_special_token_1|>',
        '<|reserved_special_token_2|>'
    ]
    for token in special_tokens:
        input_string = input_string.replace(token, '')
    return input_string
