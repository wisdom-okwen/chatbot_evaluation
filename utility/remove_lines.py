import os

PROMPT_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/prompts/"
PROMPT_PREFIX = "prompt"
START_INDEX = 320
NUM_PROMPTS = 280


def remove_last_two_lines():
    """Remove the last two lines from each prompt file."""
    for i in range(START_INDEX, START_INDEX + NUM_PROMPTS):
        file_path = os.path.join(PROMPT_DIR, f"{PROMPT_PREFIX}{i}.txt")

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}, skipping...")
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if len(lines) < 2:
            print(f"File {file_path} has less than 2 lines, skipping...")
            continue

        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines[:-2])

        print(f"Updated: {file_path}")

if __name__ == '__main__':
    remove_last_two_lines()
    print("✅ Successfully removed the last two lines from all prompt files.")
