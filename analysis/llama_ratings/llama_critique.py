import os
import csv
from sys import exit
from openai import OpenAI
from critiques import (
    SELF_ASSESSMENT_PROMPT,
    USER_ASSESSMENT_PROMPT,
    THIRD_PARTY_ASSESSMENT_PROMPT,
    THIRD_PARTY_PER_TURN_PROMPT,
    self_criteria_prompt,
    user_criteria_prompt,
    third_party_criteria_prompt
)


# Files and directories setup
OVER_ALL_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/llama_ratings/data/overall_ratings.csv"
PER_TURN_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/llama_ratings/data/per_turn_ratings.csv"
USER_CRITERIA_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/llama_ratings/data/criteria_ratings/user.csv"
OBSERVER_CRITERIA_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/llama_ratings/data/criteria_ratings/observer.csv"
SELF_CRITERIA_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/llama_ratings/data/criteria_ratings/self.csv"

CONVO_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/conversations/conv_trajectories"
CONVO_PREFIX = "trajectory"

# models
model_dict = {
    "llama": ("meta-llama/Meta-Llama-3.1-8B-Instruct", 7471),
    "mistral": ("mistralai/Mistral-7B-Instruct-v0.3", 7472),
    "phi": ("microsoft/Phi-3-small-8k-instruct", 7473)
}

MODEL = "llama"
model_name, model_port = model_dict[MODEL]

if not model_port:
    print("** Model not deployed **")
    exit()

openai_api_key = "EMPTY"
url = f"http://localhost:{model_port}/v1"

client = OpenAI(
    api_key=openai_api_key,
    base_url=url,
)


# ----------------------------------------------------- Overall Ratings ----------------------------------------------------------

overall_headers = ["Convsation_Id", "User_Rating", "Observer_Rating", "Self_Rating"]

def get_llama_overall_rating(prompt, conversation):
    """Llama prompt setup."""
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Here is the full conversation:\n\n{conversation}\n\nPlease give your rating."}
        ]
        chat_response = client.chat.completions.create(
                model=model_name,
                messages=messages
            )
        text = chat_response.choices[0].message.content
        return text
    except Exception as e:
        print("❌ Error connecting llama:", str(e))


def generate_overall_ratings():
    """Generate overall ratings using Llama model."""
    write_headers = not os.path.exists(OVER_ALL_RATINGS_FILE) or os.stat(OVER_ALL_RATINGS_FILE).st_size == 0
    with open(OVER_ALL_RATINGS_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if write_headers:
            writer.writerow(overall_headers)

        for i in range(531):
            convo_file_name = f"{CONVO_PREFIX}{i}.csv"
            convo_file_path = os.path.join(CONVO_DIR, convo_file_name)

            if not os.path.exists(convo_file_path):
                print(f"Missing: {convo_file_path}")
                continue

            with open(convo_file_path, mode="r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)
                conversation = []
                for row in reader:
                    user_msg = (row.get("User_Message") or "").strip()
                    bot_resp = (row.get("Response") or "").strip()
                    conversation.append((user_msg, bot_resp))

            formatted_convo = "\n".join([f"User: {q}\nChatbot: {a}" for q, a in conversation])

            user_rating = get_llama_overall_rating(USER_ASSESSMENT_PROMPT, formatted_convo)
            observer_rating = get_llama_overall_rating(THIRD_PARTY_ASSESSMENT_PROMPT, formatted_convo)
            self_rating = get_llama_overall_rating(SELF_ASSESSMENT_PROMPT, formatted_convo)

            writer.writerow([i, user_rating, observer_rating, self_rating])
            print(f"Rated convo {i}: User={user_rating}, Observer={observer_rating}, Self={self_rating}")



# ----------------------------------------------------- Criteria Ratings ----------------------------------------------------------

criteria = ["Clarity and Simplicity", "Relevance and Accuracy", "Tone and Supportiveness", "Adaptability", "Consistency and Flow"]
criteria_headers = ["Conversation_Id"] + [c.replace(" ", "_") for c in criteria]

persona_configs = [
    (USER_CRITERIA_RATINGS_FILE, user_criteria_prompt),
    (OBSERVER_CRITERIA_RATINGS_FILE, third_party_criteria_prompt),
    (SELF_CRITERIA_RATINGS_FILE, self_criteria_prompt)
]

def init_csv(file_path):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(criteria_headers)

def get_criteria_ratings():
    for convo_id in range(531):
        convo_file_name = f"{CONVO_PREFIX}{convo_id}.csv"
        convo_file_path = os.path.join(CONVO_DIR, convo_file_name)

        if not os.path.exists(convo_file_path):
            print(f"Missing: {convo_file_path}")
            continue

        with open(convo_file_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            conversation = [
                (row["User_Message"].strip(), row["Response"].strip())
                for row in reader if row["User_Message"] and row["Response"]
            ]
        formatted_convo = "\n".join([f"User: {q}\nChatbot: {a}" for q, a in conversation])

        for output_file, prompt_func in persona_configs:
            init_csv(output_file)

            ratings_row = [convo_id]
            for criterion in criteria:
                prompt = prompt_func(criterion)
                rating = get_llama_overall_rating(prompt, formatted_convo)
                ratings_row.append(rating)

            with open(output_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(ratings_row)
            print(f"Logged {prompt_func.__name__.split('_')[0]} ratings for convo {convo_id}")


# ----------------------------------------------------- Per Turn Ratings ----------------------------------------------------------
turns = ["Conversation_ID"] + [f"Turn_{i}" for i in range(1, 26)]

def get_per_turn_ratings():
    init_csv(PER_TURN_RATINGS_FILE)

    for i in range(531):
        convo_file_name = f"{CONVO_PREFIX}{i}.csv"
        convo_file_path = os.path.join(CONVO_DIR, convo_file_name)

        if not os.path.exists(convo_file_path):
            print(f"Missing: {convo_file_path}")
            continue

        with open(convo_file_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            conversation = [
                (row["User_Message"].strip(), row["Response"].strip())
                for row in reader
                if row["User_Message"] and row["Response"]
            ]

        ratings = [i]
        for idx, (user_msg, bot_resp) in enumerate(conversation[:25]):
            turn_text = f"User: {user_msg}\nChatbot: {bot_resp}"
            rating = get_llama_overall_rating(THIRD_PARTY_PER_TURN_PROMPT, turn_text)
            ratings.append(rating)

        with open(PER_TURN_RATINGS_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(ratings)
        print(f"Rated all turns for conversation {i}")


if __name__ == '__main__':
    generate_overall_ratings()
    get_criteria_ratings()
    get_per_turn_ratings()