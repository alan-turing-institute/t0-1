import logging

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

logging.basicConfig(level=logging.INFO)
logging.info(f"CUDA available: {torch.cuda.is_available()}")
logging.info(f"CUDA device count: {torch.cuda.device_count()}")

DEVICE = "cuda"
model_name = "ckpts/t0_r1-20250417_114011"
# model_name = "simplescaling/s1.1-32B"

logging.info(f"Loading model {model_name}...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
logging.info(f"Model loaded on {model.device}")

logging.info(f"Loading tokenizer for {model_name}...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
logging.info(f"Tokenizer loaded")


system = """You are a clinical AI assistant.

You will be given a description of their symptoms and some retieved context that could be relevant to those symptoms

You need to suggest the most likely condition and the level of severity.

You should decide one of five options for severity:
* Ambulance:  Immediate life-threatening danger; treatment needed en route to the hospital
* A&E: Emergency hospital treatment required
* Urgent Primary Care: patient should be seen today, by a GP, urgent care centre, or similar
* Routine GP appointment: patient should be seen at some point, but this can wait for several days
* Self-care: issue can be handled at home and/or with over-the-counter medication.

Importantly, if you think that the condition is not listed, please use "inconclusive" for the condition."""

prompt = """A patient has given the following description of their symptoms:
"I've been feeling perpetually anxious and overwhelmed, and it's gotten worse over the past week. My chest feels tight, and I’ve had difficulty catching my breath at times—I can't tell if it's just anxiety or my asthma acting up. I’ve also had near-constant headaches and occasional dizziness when I try to stand. My heart feels like it’s racing, and I’ve been sweating excessively, even when I’m sitting still. On top of that, I haven't been able to sleep properly for days, and I’m starting to feel extremely tearful and hopeless because I can’t get anything done at work or even concentrate on basic tasks. I spent half the night awake last night thinking something terrible is going to happen, and this morning I’ve been having intrusive thoughts about hurting myself. I haven't harmed myself, but I’m scared I might. My sister is worried and thinks I need help right away. Please advise me on what to do next."

This is a summary of their demographics:
{'age': 28, 'sex': 'Female', 'occupation': 'Retail worker', 'social_support': 'My sister is here to help me, but I live alone most of the time.', 'medical_history': "I have mild asthma and occasionally use an inhaler. No other significant medical issues, but I sometimes feel overwhelmed when it's humid."}

Using the sources and context provided, submit the condition and the severity level in the format: "(condition, severity)". Do not provide any explanation to the output, only your final answer.

Remember that the condition must either be one of ['stress-anxiety-depression', 'medically-unexplained-symptoms', 'panic-disorder', 'generalised-anxiety-disorder'] or "inconclusive" if you think that the condition is not listed.
Remember that the severity level must be one of ["Self-care", "Routine GP appointment", "Urgent Primary Care", "A&E", "Ambulance"]."""

messages = [
    {"role": "system", "content": system},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

logging.info(f"Input: {text}")
logging.info("Generating response...")
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=2048
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=False)[0]

logging.info(f"Response: {response}")