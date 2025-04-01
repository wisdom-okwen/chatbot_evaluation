import os
import csv
from critiques import (
    get_gpt_overall_rating, 
    SELF_ASSESSMENT_PROMPT, 
    SELF_PER_TURN_PROMPT, 
    USER_ASSESSMENT_PROMPT, 
    USER_PER_TURN_PROMPT, 
    THIRD_PARTY_ASSESSMENT_PROMPT, 
    THIRD_PARTY_PER_TURN_PROMPT
)


OVER_ALL_RATINGS_FILE = "/playpen-ssd/wokwen/projects/chatbot_eval/overall_ratings.csv"
CONVO_DIR = "../conv_trajectories/conv_trajectories"
CONVO_PREFIX = "trajectory"


headers = ["Convsation_Id", "User_Rating", "Observer_Rating", "Self_Rating"]

# with open(OVER_ALL_RATINGS_FILE, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(headers)

       
def generate_overall_ratings():

    write_headers = not os.path.exists(OVER_ALL_RATINGS_FILE) or os.stat(OVER_ALL_RATINGS_FILE).st_size == 0
    with open(OVER_ALL_RATINGS_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if write_headers:
            writer.writerow(headers)

        for i in range(530):
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

            user_rating = get_gpt_overall_rating(USER_ASSESSMENT_PROMPT, formatted_convo)
            observer_rating = get_gpt_overall_rating(THIRD_PARTY_ASSESSMENT_PROMPT, formatted_convo)
            self_rating = get_gpt_overall_rating(SELF_ASSESSMENT_PROMPT, formatted_convo)

            writer.writerow([i, user_rating, observer_rating, self_rating])
            print(f"Rated convo {i}: User={user_rating}, Observer={observer_rating}, Self={self_rating}")

def get_per_turn_ratings():
    pass


if __name__ == '__main__':
    generate_overall_ratings()