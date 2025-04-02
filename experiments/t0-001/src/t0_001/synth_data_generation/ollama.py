import ollama

# basic function to prompt the model
def get_response_from_ollama_model(prompt, model="gemma3:1b"):
    response = ollama.generate(model=model, prompt=prompt)
    return response["response"]
