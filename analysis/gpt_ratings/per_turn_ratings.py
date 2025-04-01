import os
import csv
from critiques import get_gpt_overall_rating, THIRD_PARTY_PER_TURN_PROMPT

PER_TURN_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/per_turn_ratings.csv"
CONVO_DIR = "../conv_trajectories/conv_trajectories"
CONVO_PREFIX = "trajectory"

turns = ["Conversation_ID"] + [f"Turn_{i}" for i in range(1, 26)]

def init_csv(file_path):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(turns)

def get_per_turn_ratings():
    init_csv(PER_TURN_RATINGS_FILE)

    for i in range(355, 531):
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
            rating = get_gpt_overall_rating(THIRD_PARTY_PER_TURN_PROMPT, turn_text)
            ratings.append(rating)

        with open(PER_TURN_RATINGS_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(ratings)
        print(f"Rated all turns for conversation {i}")


if __name__ == '__main__':
    get_per_turn_ratings()

