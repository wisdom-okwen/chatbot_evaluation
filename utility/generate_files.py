import os

def append_to_prompt_files():
    """ Append a specific line to all prompt files starting from prompt240.txt. """
    
    # Directory where prompt files are stored
    PROMPT_DIR = "../wokwen/projects/chatbot_eval/prompts/"
    PROMPT_PREFIX = "prompt"
    START_INDEX = 240  # Start modifying from prompt240.txt
    TOTAL_PROMPTS = 500  # Assuming you have 500 prompts

    line_to_add = "\n***Your job is to just ask questions***\n"

    for i in range(START_INDEX, TOTAL_PROMPTS + 1):
        prompt_file_name = f"{PROMPT_PREFIX}{i}.txt"
        prompt_file_path = os.path.join(PROMPT_DIR, prompt_file_name)

        if os.path.exists(prompt_file_path):
            with open(prompt_file_path, "a", encoding="utf-8") as file:  # Open in append mode
                file.write(line_to_add)
            print(f"Updated: {prompt_file_path}")
        else:
            print(f"File not found: {prompt_file_path}")  # Just in case a file is missing

if __name__ == "__main__":
    append_to_prompt_files()


def generate_prompt_files():
    # Directory where prompt files will be saved
    PROMPT_DIR = "../wokwen/projects/chatbot_eval/prompts/"
    PROMPT_PREFIX = "prompt"

    # Ensure the directory exists
    os.makedirs(PROMPT_DIR, exist_ok=True)

    # Sample prompts to be used in the files (You can modify or expand this list)
    sample_prompts = [
        "What are the benefits of using PrEP?",
        "Is PrEP safe for long-term use?",
        "How effective is PrEP in preventing HIV?",
        "Can I take PrEP if I am pregnant?",
        "What are the common side effects of PrEP?",
        "How do I start taking PrEP?",
        "Does PrEP protect against other STDs?",
        "What happens if I miss a dose of PrEP?",
        "How much does PrEP cost?",
        "Where can I get PrEP?",
        "Do I need to take PrEP every day?",
        "Can I stop taking PrEP anytime?",
        "Is PrEP available without a prescription?",
        "How long does PrEP take to become effective?",
        "Can PrEP interact with other medications?",
        "Is PrEP covered by insurance?",
        "Does PrEP affect fertility?",
        "Can men and women both use PrEP?",
        "How frequently should I get tested while on PrEP?",
        "Are there any alternatives to PrEP for HIV prevention?",
        "Do I need to take PrEP every day?",
        "Can I stop taking PrEP anytime?",
        "Is PrEP available without a prescription?",
        "How long does PrEP take to become effective?",
        "Can PrEP interact with other medications?",
        "Is PrEP covered by insurance?",
        "Does PrEP affect fertility?",
        "Can men and women both use PrEP?",
        "How frequently should I get tested while on PrEP?",
        "Are there any alternatives to PrEP for HIV prevention?"
    ]

    # Generate the prompt files
    for i in range(89, 93):
        prompt_file_name = f"{PROMPT_PREFIX}{i}.txt"
        prompt_file_path = os.path.join(PROMPT_DIR, prompt_file_name)
        
        with open(prompt_file_path, 'w', encoding='utf-8') as prompt_file:
            # prompt_file.write(sample_prompts[i])
            pass

    print("Prompt files generated successfully in:", PROMPT_DIR)


def generate_conv_trajectory_files():
    CONVO_DIR = "../wokwen/projects/chatbot_eval/conv_trajectories/"
    CONVO_PREFIX = "trajectory"

    os.makedirs(CONVO_DIR, exist_ok=True)

    for i in range(20, 28):
        conv_file_name = f"{CONVO_PREFIX}{i}.csv"
        conv_file_path = os.path.join(CONVO_DIR, conv_file_name)
        
        with open(conv_file_path, 'w', encoding='utf-8') as conv_file:
            # prompt_file.write(sample_prompts[i])
            pass

    print("Prompt files generated successfully in:", CONVO_DIR)


if __name__ == '__main__':
    # generate_conv_trajectory_files()
    # generate_prompt_files()
    append_to_prompt_files()