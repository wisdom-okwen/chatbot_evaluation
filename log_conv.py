import os
import random
import csv
from datetime import datetime
from .utility.gpt_seeker import seeker
from shesprepared.gpt1 import get_gpt_response

# Directories and prefixes
CONVO_DIR = "../wokwen/projects/chatbot_eval/conv_trajectories/"
CONVO_PREFIX = "trajectory"
PROMPT_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/prompts/"
PROMPT_PREFIX = "prompt"

NUM_QUERIES = 25

headers = ["User_Message", "Response", "Response_Time", "Temperature"]

def initialize_convo_csv(file_path):
    """Initialize a CSV file for conversation logging."""
    if not os.path.exists(file_path):
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            writer.writerow(headers)

def log_trajectories():
    """Logs multiple conversation trajectories per prompt."""
    os.makedirs(CONVO_DIR, exist_ok=True)
    os.makedirs(PROMPT_DIR, exist_ok=True)

    for idx, i in enumerate(range(511, 511), start=1):
        prompt_file_name = f"{PROMPT_PREFIX}{i}.txt"
        prompt_file_path = os.path.join(PROMPT_DIR, prompt_file_name)

        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as prompt_file:
                prompt = prompt_file.read().strip()
        except FileNotFoundError:
            print(f"Prompt file not found: {prompt_file_path}")
            continue

        if not prompt:
            print(f"Prompt file {prompt_file_path} is empty, skipping...")
            continue

        convo_file_name = f"{CONVO_PREFIX}{i}.csv"
        convo_file_path = os.path.join(CONVO_DIR, convo_file_name)

        initialize_convo_csv(convo_file_path)

        conversation_history = []

        for j in range(NUM_QUERIES):
            temperature = round(random.uniform(0.5, 1), 2)

            history_text = "\n".join(
                [f"User: {entry['user']}\nChatbot: {entry['chatbot']}" for entry in conversation_history[-10:]]
            )

            seeker_query = seeker(prompt, history_text, temperature)

            start_time = datetime.now()
            response_time = (datetime.now() - start_time).total_seconds()

            try:
                chatbot_response = get_gpt_response(seeker_query)
            except Exception as e:
                chatbot_response = f"Error in chatbot response: {e}"

            conversation_history.append({"user": seeker_query, "chatbot": chatbot_response})

            with open(convo_file_path, mode="a", newline="", encoding="utf-8") as convo_file:
                writer = csv.writer(convo_file, quoting=csv.QUOTE_ALL)
                writer.writerow([
                    seeker_query,
                    chatbot_response,
                    round(response_time, 2),
                    temperature,
                ])

        print(f"Logged conversation trajectory: {convo_file_path}")

        # Pause for 1 minute after every 6 iterations
        if idx % 6 == 0:
            print("Pausing for 1 minute to avoid overloading...")
            # time.sleep(60)
            exit()

if __name__ == '__main__':
    log_trajectories()
