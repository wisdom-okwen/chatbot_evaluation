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

# Store some history of conversation
llama_history = []

MAX_HISTORY_LENGTH = 2

# Load decision-aid content
with open('decision-aid-content.txt', 'r', encoding='utf-8') as file:
    decision_aid_content = file.read()


def word_count(text):
    return len(text.split())


def token_count(text):
    # Approximate token count by splitting on spaces. OpenAI has a more precise tokenization tool.
    return len(text.split())


def is_complete_response(text):
    return text.strip()[-1] in [".", "!", "?"]  # Check if the response ends with proper punctuation


def is_complete_response(text):
    return text.strip()[-1] in [".", "!", "?"]  # Check if the response ends with proper punctuation


MAX_WORDS = 600
MAX_TOKENS = 600

def enforce_limits(response):
    words = response.split()
    tokens = token_count(response)

    if len(words) > MAX_WORDS or tokens > MAX_TOKENS:
        truncated_response = " ".join(words[:MAX_WORDS]) + "..."
        return truncated_response + "\n\nPlease let me know if you'd like more details!"
    return response


def get_llama_response(user_input):
    """ Function to get GPT's response based on user input, using detailed prompts """
    global llama_history, client, model_name

    messages = [
        {"role": "system", "content": (
            "You are ShesPrEPared, a friendly assistant focused on HIV prevention and PrEP counseling for women.\n\n"
            "Your tasks:\n"
            "- Provide concise, evidence-based information on HIV prevention and care.\n"
            "- Use decision aid content and conversation history to inform responses.\n\n"
            "Guidelines:\n"
            "- Use non-stigmatizing, affirming language.\n"
            "- Avoid conducting risk assessments or labelling as 'risky'.\n"
            # "- Avoid excessive detail; limit responses to 50-100 tokens or 70-120 words.\n"
            "Provide concise, accurate, and user-centered responses that avoid stigmatizing terms, focus on practical prevention options, and emphasize affirming, actionable guidance tailored to the user's needs."
            "- Format responses with clear bullet points or short sentences.\n\n"
            "Response strategy:\n"
            "1. Identify the user’s main concern.\n"
            "2. Reference decision aid content for accurate information.\n"
            "3. Provide clear, actionable responses in bullet points or 1-2 sentences.\n"
            "4. Redirect politely if the user diverges from HIV-related topics.\n\n"
            "Example:\n"
            "**Input:** 'What is HIV?'\n"
            "**Response:**\n"
            "- HIV (human immunodeficiency virus) attacks the immune system, targeting CD4 cells.\n"
            "- Untreated, it can lead to AIDS, severely weakening the immune system.\n"
            "- Main transmission modes include unprotected sex, sharing needles, and mother-to-child transmission.\n\n"
            f"Reference materials:\n- Decision Aid Content: {decision_aid_content}\n- Conversation History: {llama_history[-MAX_HISTORY_LENGTH:]}"
        )},
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
        if not is_complete_response(response_message):
            response_message += " (Response truncated. Please ask for more details.)"
        
        response_message = enforce_limits(response_message)
        llama_history.append({"user": user_input, "bot": response_message})
        return response_message
    except Exception as e:
        return f"Llama experienced an internal error: {str(e)}"

    
if __name__ == '__main__':
    print("Enter your input: \n")
    user_input = input()
    print(get_llama_response(user_input))
    print('\n\n')
    print(llama_history)