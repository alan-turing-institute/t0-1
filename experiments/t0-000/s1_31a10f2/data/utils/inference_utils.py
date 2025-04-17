from openai import OpenAI
import time
import anthropic
from typing import List, Dict
from data.utils.io_utils import set_openai_private_key, set_anthropic_private_key


def calc_price(model, usage):
    """
    Output the price of the inference in dollars.
    """
    cached_tokens = usage.prompt_tokens_details['cached_tokens']
    non_cached_tokens = usage.prompt_tokens - cached_tokens
    output_tokens = usage.completion_tokens
    if model == "gpt-4o":
        input_price = (non_cached_tokens * 2.50 + cached_tokens * 1.25) / 1_000_000
        output_price = output_tokens * 10.00 / 1_000_000
    elif model == "gpt-4o-mini":
        input_price = (non_cached_tokens * 0.150 + cached_tokens * 0.075) / 1_000_000
        output_price = output_tokens * 0.600 / 1_000_000
    elif model == "o1-mini":
        input_price = (non_cached_tokens * 3.00 + cached_tokens * 1.50) / 1_000_000
        output_price = output_tokens * 12.00 / 1_000_000
    elif model == "o1-preview":
        input_price = (non_cached_tokens * 15.00 + cached_tokens * 7.50) / 1_000_000
        output_price = output_tokens * 60.00 / 1_000_000
    elif model == "claude-3-5-sonnet":
        input_price = (non_cached_tokens * 3.00 + cached_tokens * 0.30) / 1_000_000
        output_price = output_tokens * 15.00 / 1_000_000
    else:
        raise ValueError(f"Unsupported model: {model}")
    return input_price + output_price

def _gptqa(prompt: str, openai_model_name: str, system_message: str, json_format: bool):
    client = OpenAI()
    if openai_model_name.startswith('o1'):
        assert json_format == False, "o1 model does not support json format"
        completion = client.chat.completions.create(
                model=openai_model_name,
                messages=[
                    {"role": "user",
                     "content": system_message + "\n\n" + prompt},
                ])
    else:
        if json_format:
            completion = client.chat.completions.create(
                model=openai_model_name,
                response_format={ "type": "json_object" },
                messages=[
                    {"role": "system",
                    "content": system_message},
                    {"role": "user",
                    "content": prompt},
                ])
        else:
            completion = client.chat.completions.create(
                model=openai_model_name,
                messages=[
                    {"role": "system",
                    "content": system_message},
                    {"role": "user",
                    "content": prompt},
                ])
    return completion.choices[0].message.content, completion.usage

def _claudeqa(prompt: str, system_message: str):
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        system=system_message,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return message.content[0].text, message.usage

def apiqa(prompt: str, model_name: str, system_message: str, json_format: bool = True):
    completion = None
    while completion is None:
        try:
            if model_name == 'claude-3-5-sonnet-20241022':
                set_anthropic_private_key()
                assert json_format == False, "Claude does not support json format"
                completion, usage = _claudeqa(prompt, system_message)
            else:
                set_openai_private_key()
                completion, usage = _gptqa(prompt, model_name, system_message, json_format)
        except Exception as e:
            print(f"Exception: {str(e)}")
            time.sleep(60)
    
    return completion, usage

def claude_multi_round(system_prompt: str, messages: List[Dict[str, str]]):
    completion = None
    while completion is None:
        try:
            set_anthropic_private_key()
            client = anthropic.Anthropic()
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8192,
                system=system_prompt,
                messages=messages
            )
            completion = message.content[0].text
        except Exception as e:
            print(f"Exception: {str(e)}")
            time.sleep(60)
    return completion, message.usage