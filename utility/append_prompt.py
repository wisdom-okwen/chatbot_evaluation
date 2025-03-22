import os

# Directory where prompt files are stored
PROMPT_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/prompts/"
PROMPT_PREFIX = "prompt"
START_INDEX = 94  # First file should be prompt94.txt
NUM_PROMPTS = 500  # Total number of prompts

# Lines to append
APPEND_LINES = [
    "\n***Be sure to act as an information seeker only and not information provider***\n",
    "***Questions should be specific to your profile (age, gender, sexual orientation, education level, nationality, primary concern, language)***\n"
]

def append_lines_to_prompts():
    """Append specified lines to all prompt files if they are not already present."""
    for i in range(START_INDEX, START_INDEX + NUM_PROMPTS):
        file_path = os.path.join(PROMPT_DIR, f"{PROMPT_PREFIX}{i}.txt")

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}, skipping...")
            continue

        # Read existing content
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Check if lines are already appended
        if APPEND_LINES[0].strip() in content and APPEND_LINES[1].strip() in content:
            print(f"File {file_path} already updated, skipping...")
            continue

        # Append lines if they are not present
        with open(file_path, "a", encoding="utf-8") as file:
            file.writelines(APPEND_LINES)

        print(f"Updated: {file_path}")

if __name__ == '__main__':
    append_lines_to_prompts()
    print("✅ All prompt files have been updated successfully.")
