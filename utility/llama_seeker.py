from openai import OpenAI
from .server_info import model_dict


# Setup open source llama 3.1 8B Instruct
MODEL = "llama" # select among "llama 3.1 8B" model
model_name, model_port = model_dict[MODEL]

if model_port == -1:
    print("** Model not deployed **")
    exit()

openai_api_key = "EMPTY"
url = f"http://152.2.134.51:{model_port}/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=url,
)

def llama_seeker(prompt, temperature):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Llama experienced an internal error: {str(e)}"
    
if __name__ == '__main__':
    # user_input = input()
    sample_prompt = """
    You're an information seeker and want to assume the role of someone who is interested in PrEP but has many concerns. 
    Start by asking about the basics of PrEP, then dive deeper into topics such as effectiveness, side effects, adherence challenges, and cost. 
    You occasionally express doubts and ask for reassurance before considering taking PrEP.
    Be sure to ask at most 2 but at least 1 question(s).
    """
    print(llama_seeker(sample_prompt, 0.7))
    print('\n\n')
