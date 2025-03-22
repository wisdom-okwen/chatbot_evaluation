from sys import exit
from openai import OpenAI


model_dict = {
    "llama": ("meta-llama/Meta-Llama-3.1-8B-Instruct", 7471),
    "mistral": ("mistralai/Mistral-7B-Instruct-v0.3", 7472),
    "phi": ("microsoft/Phi-3-small-8k-instruct", 7473)
}

MODEL = "llama"
model_name, model_port = model_dict[MODEL]

if model_port == -1:
    print("** Model not deployed **")
    exit()

openai_api_key = "EMPTY"
url = f"http://localhost:{model_port}/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=url,
)

def get_llama_overall_rating():
    chat_response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Introduce yourself concisely"},
                ]
            )

    text = chat_response.choices[0].message.content
    print(text)

if __name__ == '__main__':
    get_llama_overall_rating()