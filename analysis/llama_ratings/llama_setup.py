from openai import OpenAI
from server_info import model_dict
# from sample import sample_interaction

# Setup open source llama 3.1 8B Instruct
MODEL = "llama" # select among "llama 3.1 8B" model
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

def get_llama_response(user_input):
    """ Function to get GPT's response based on user input, using detailed prompts """

    messages = [
        {"role": "system", 
         "content": "You are ShesPrEPared, a friendly assistant focused on HIV prevention and PrEP counseling for women.\n\n"
        },
        {"role": "user", "content": user_input}
    ]


    try:
        chat_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=500,
            temperature=0.5,
            # stream=True
        )

        response_message = chat_response.choices[0].message.content

        # Post-generation checks
        return response_message
    except Exception as e:
        return f"Llama experienced an internal error: {str(e)}"

    
if __name__ == '__main__':
    print("Enter your input: \n")
    user_input = input()
    print(get_llama_response(user_input))
    print('\n\n')
