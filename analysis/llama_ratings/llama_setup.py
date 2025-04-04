import os
from openai import OpenAI
from huggingface_hub import login
from dotenv import load_dotenv
import torch
from transformers import (
    pipeline,
    AutoModelForCausalLM,
    AutoTokenizer
)


load_dotenv()
HF_API_KEY = os.getenv('HUGGINGFACE_TOKEN_ID')


login(HF_API_KEY)

def get_llama_32_response(messages):
    """Generate response from downloaded model."""
    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    
    # Load model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # Create pipeline
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )

    # Generate text
    outputs = pipe(
        messages,
        max_new_tokens=256,
        do_sample=True,
        temperature=0.75,
    )
    
    return outputs[0]["generated_text"]
    
if __name__ == '__main__':
    print("Enter your input: \n")
    messages = "What are some strategies for managing anxiety?"
    response = get_llama_32_response(messages)
    print(response)
