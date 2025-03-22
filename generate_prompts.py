import os
import random
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

# Set OpenAI API key
api_key = os.getenv("PERSONAL_OPENAI_KEY")
if not api_key:
    raise ValueError("PERSONAL_OPENAI_KEY environment variable is not set.")

client = OpenAI(api_key=api_key)

# Directory to save prompts
# PROMPT_DIR = "/prompts/"
# HISTORY_FILE = "prompt_history.txt"


PROMPT_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/prompts/"
HISTORY_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/prompt_history.txt"

os.makedirs(PROMPT_DIR, exist_ok=True)

# Number of prompts to generate
NUM_PROMPTS = 10
START_INDEX = 511


languages = ["English", "French", "English", "Spanish", "English", "Portuguese", "English","Swahili", "Dutch", "English"]


EXAMPLE_PROMPT_EDGE_CASE = """
You are an information seeker who is in an **unusual situation** regarding PrEP.  
Your concerns are **specific, urgent, or uncommon**, making it hard to find clear answers.  

- **Situation:** You are a 42-year-old married person who recently discovered that your spouse had an affair.  
- **Mental state:** You feel betrayed, confused, and anxious about your health.  
- **Primary concern about PrEP:** You are unsure if PrEP is appropriate for someone in a committed relationship.  
- **Barriers to access:** You live in a small town where discussing HIV prevention is taboo.  
- **Socio-economic status:** Middle-income
- **Language of conversation:** English  

Question should be prioritized towards primary concern about PrEP, sexual orientation, socio-economic status, barriers, situation and mental state.

You may start by asking:
"Qual é a eficácia do PrEP na prevenção do HIV e quais são os efeitos colaterais que posso esperar?"  

As the conversation progresses, you might follow up with:  
"Quem é um bom candidato para o PrEP? Eu me encaixo nesse perfil?"  

Your questions should **reflect deep personal conflict, social stigma, and access challenges**.  
Keep each question **specific, realistic, and reflective of someone struggling with uncertainty.**  
"""

def load_prompt_history():
    """Load existing prompts from history file to prevent repetition."""
    if not os.path.exists(HISTORY_FILE):
        return set()

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        return set(file.read().split("\n\n"))
    

def save_prompt_to_history(prompt):
    """Save a new unique prompt to the history file."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        file.write(prompt + "\n\n")


def generate_prompt():
    """Generate a structured PrEP conversation prompt using OpenAI GPT."""
    language = random.choice(languages)
    # language = "English"
    history = load_prompt_history()

    prompt_request = (
        "Generate a unique conversation prompt for a user seeking information about PrEP. "
        "First, create a random user profile by generating details for nationality, age, gender, "
        "socio-economic background, primary concern, and language of conversation. "
        "Then, structure the conversation like the example below, starting with cautious curiosity and progressing to open engagement. "
        "Ensure markdown formatting for clarity.\n\n"
        f"The user can speak {language}"
        "Prompts should be concise and concentrated as much as possible with very few examples.\n"
        f"Example Structure:\n{EXAMPLE_PROMPT_EDGE_CASE}\n\n"
        "Your example questions should not be formatted and should follow exactly the example structure given.\n"
        f"**Your responses should model the example given and should not give a starting question or direction of conversation**\n"
        f"Take note of this history and don't repeat any sentence from it: {history}"
        "Now generate a fully fleshed-out, unique prompt following this structure."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt_request}],
            max_tokens=450,
            temperature=0.85
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating prompt: {str(e)}"


if __name__ == '__main__':
    generated_count = 0
    for i in range(START_INDEX, START_INDEX + NUM_PROMPTS):
        prompt_text = generate_prompt()
        save_prompt_to_history(prompt_text)

        file_path = os.path.join(PROMPT_DIR, f"prompt{i}.txt")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(prompt_text)

        print(f"Generated and saved: {file_path}")
        generated_count += 1

    print(f"Successfully generated {generated_count} unique prompts starting from prompt{START_INDEX}.txt")

