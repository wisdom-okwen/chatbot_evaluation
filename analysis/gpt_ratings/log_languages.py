import os
import openai  # Correct import
from dotenv import load_dotenv
import pandas as pd

overall_ratings_file = '/playpen-ssd/wokwen/projects/chatbot_eval/analysis/data/overall_ratings.csv'
conv_dir = '/playpen-ssd/wokwen/projects/chatbot_eval/conversations/conv_trajectories'
trajectory_prefix = "trajectory"

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = API_KEY  # Correct initialization

def log_language():
    df = pd.read_csv(overall_ratings_file)
    if 'Language' not in df.columns:
        df['Language'] = None  # Add the new column if it doesn't exist
    
    df['Language'] = df['Language'].astype(str)
    for i in range(len(df)):  # Looping through all rows in the CSV file
        file_name = f"{trajectory_prefix}{i}.csv"
        file_path = os.path.join(conv_dir, file_name)
        
        try:
            with open(file_path, 'r') as file:
                conversation = file.read()
        except FileNotFoundError:
            print(f"Prompt file not found: {file_name}")
            continue

        prompt = f"""
        I'll give you a conversation between a chatbot and a user. You're to log the language used in the given conversation.
        If there are multiple languages used, log the primary language of communication. \n
        **You must return just the language, no explanation whatsoever.**\n
        Example response: English
        """
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": conversation}
        ]
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=50,
                temperature=0.3
            )
            gpt_response = response.choices[0].message.content.strip()
            df.at[i, "Language"] = gpt_response
        except Exception as e:
            print(f"GPT experienced an internal error for conversation {i}: {str(e)}")
            continue

    df.to_csv(overall_ratings_file, index=False)
    print("Language logging completed successfully.")

if __name__ == "__main__":
    log_language()
