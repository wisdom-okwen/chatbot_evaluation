import os
import csv
from critiques import (
    user_criteria_prompt, 
    self_criteria_prompt, 
    third_party_criteria_prompt, 
    get_gpt_overall_rating
)


USER_CRITERIA_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/criteria_ratings/user.csv"
OBSERVER_CRITERIA_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/criteria_ratings/observer.csv"
SELF_CRITERIA_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/criteria_ratings/self.csv"

CONVO_DIR = "../conv_trajectories/conv_trajectories"
CONVO_PREFIX = "trajectory"

criteria = ["Clarity and Simplicity", "Relevance and Accuracy", "Tone and Supportiveness", "Adaptability", "Consistency and Flow"]
headers = ["Conversation_Id"] + [c.replace(" ", "_") for c in criteria]

persona_configs = [
    (USER_CRITERIA_RATINGS_FILE, user_criteria_prompt),
    (OBSERVER_CRITERIA_RATINGS_FILE, third_party_criteria_prompt),
    (SELF_CRITERIA_RATINGS_FILE, self_criteria_prompt)
]

def init_csv(file_path):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

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
                rating = get_gpt_overall_rating(prompt, formatted_convo)
                ratings_row.append(rating)

            with open(output_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(ratings_row)
            print(f"Logged {prompt_func.__name__.split('_')[0]} ratings for convo {convo_id}")


if __name__ == '__main__':
    get_criteria_ratings()
