"""Generate new conversation from low rated conversations."""
import os
import csv
import pandas as pd
import random
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from chatbot_eval.utility.gpt_seeker import seeker
from shesprepared.gpt import get_gpt_response
from chatbot_eval.analysis.conv_generators.log_conv import initialize_convo_csv
from chatbot_eval.analysis.utility import (
    get_low_criteria_rating_ids,
    get_low_overall_rating_ids,
    get_low_per_turn_rating_ids
)


load_dotenv()

# GPT Setup
api_key = os.getenv('OPENAI_API_KEY')
gpt_client = OpenAI(
    api_key=api_key
)

# Llama setup
model_dict = {
    "llama": ("meta-llama/Meta-Llama-3.1-8B-Instruct", 7471),
    "mistral": ("mistralai/Mistral-7B-Instruct-v0.3", 7472),
    "phi": ("microsoft/Phi-3-small-8k-instruct", 7473)
}
MODEL = "llama"
model_name, model_port = model_dict[MODEL]
url = f"http://localhost:{model_port}/v1"

llama_client = OpenAI(
    api_key="EMPTY",
    base_url=url,
)

# Load ratings files
GPT_OVERALL_RATINGS = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/gpt_ratings/data/overall_ratings.csv"
LLAMA_OVERALL_RATINGS = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/llama_ratings/data/overall_ratings.csv"
GPT_CRITERIA_RATINGS = "/playpen-ssd/wokwen/projects/chatbot_eval/analysis/gpt_ratings/data/criteria_ratings"

# Setup directories
PREV_CONV_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/conversations/conv_trajectories"
GPT_CONVO_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/re_eval/gpt/new_convs" 
GPT_CRITERIA_CONVO_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/re_eval1/gpt/new_criteria_convs" 
LLAMA_CONV_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/re_eval/llama/new_convs"
PREV_GPT_RATINGS_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/re_eval/llama/new_convs"
PROMPT_DIR = "/playpen-ssd/wokwen/projects/chatbot_eval/prompts"

os.makedirs(GPT_CONVO_DIR, exist_ok=True)
os.makedirs(LLAMA_CONV_DIR, exist_ok=True)

low_rated_overall_convs = get_low_overall_rating_ids() # list of conv ids
low_rated_criteria_convs = get_low_criteria_rating_ids() # dict of dicts
low_rated_per_turn_convs = get_low_per_turn_rating_ids() # list of dictionaries

# System prompt for llama and gpt
system_prompt = (
    "You are an expert chatbot evaluator. "
    "Given a conversation transcript and its numeric/textual ratings, "
    "produce a concise, single‑paragraph summary that: "
    "1) highlights what went well, 2) pinpoints weaknesses or 'loopholes', "
    "and 3) offers actionable suggestions for improvement."
)

NUM_QUERIES = 25

# I want to generate new conversation for conversations with lower overall ratings 
def gpt_summalyzer(conv, ratings):
    """
    Gets a one‑paragraph feedback summary of the conversation + ratings.
    - Uses GPT.
    """
    user_prompt = (
        f"Conversation:\n{conv}\n\n"
        f"Ratings:\n{ratings}\n\n"
        "Please provide a single‑paragraph summary analysis."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
    ]
    try:
        response = gpt_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600,
            temperature=0.65
        )
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        return f"GPT experienced an internal error: {e}"
    

def llama_summalyzer(conv, ratings):
    """
    Gets a one‑paragraph feedback summary of the conversation + ratings.
    Uses Llama 3.1 8B
    """
    user_prompt = (
        f"Conversation:\n{conv}\n\n"
        f"Ratings:\n{ratings}\n\n"
        "Please provide a single‑paragraph summary analysis."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
    ]
    try:
        response = llama_client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=600,
            temperature=0.65
        )
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        return f"GPT experienced an internal error: {e}"
    
def gpt_summalyzer(conv: str, rating: float, criterion: str) -> str:
    """
    Gets a single‐paragraph feedback summary for one criterion.
    """
    user_prompt = (
        f"Conversation:\n{conv}\n\n"
        f"Criterion: {criterion}\n"
        f"Rating: {rating}\n\n"
        "Please provide a single‑paragraph summary analysis focusing on this criterion."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
    ]
    resp = gpt_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=400,
        temperature=0.65
    )
    return resp.choices[0].message.content.strip()


def llama_summalyzer(conv: str, rating: float, criterion: str) -> str:
    """
    Gets a single‐paragraph feedback summary for one criterion using Llama.
    """
    user_prompt = (
        f"Conversation:\n{conv}\n\n"
        f"Criterion: {criterion}\n"
        f"Rating: {rating}\n\n"
        "Please provide a single‑paragraph summary analysis focusing on this criterion."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt}
    ]
    resp = llama_client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_tokens=400,
        temperature=0.65
    )
    return resp.choices[0].message.content.strip()

def generate_new_convs():
    df_ratings = pd.read_csv(GPT_OVERALL_RATINGS)

    for conv_id in low_rated_overall_convs:
        row = df_ratings[df_ratings["Convsation_Id"] == conv_id]
        if row.empty:
            print(f"[WARN⚠️] No ratings for Conversation_Id={conv_id}")
            continue
        ratings = row.iloc[0].to_dict()

        conv_path = os.path.join(PREV_CONV_DIR, f"trajectory{conv_id}.csv")
        if not os.path.exists(conv_path):
            print(f"[WARN⚠️] Missing trajectory file: {conv_path}")
            continue
        conv_text = open(conv_path, encoding="utf8").read()

        try:
            gpt_summary   = gpt_summalyzer(conv_text, ratings)
            llama_summary = llama_summalyzer(conv_text, ratings)
        except Exception as e:
            print(f"[ERROR❌] Summarizer failed for {conv_id}: {e}")
            continue

        prompt_path = os.path.join(PROMPT_DIR, f"prompt{conv_id}.txt")
        if not os.path.exists(prompt_path):
            print(f"[WARN⚠️] Missing prompt file: {prompt_path}")
            continue
        base_prompt = open(prompt_path, encoding="utf8").read()

        convo_file = os.path.join(GPT_CONVO_DIR, f"trajectory{conv_id}.csv")
        initialize_convo_csv(convo_file)

        conversation_history = []
        for turn in range(NUM_QUERIES):
            temperature = round(random.uniform(0.5, 1.0), 2)

            history_text = "\n".join(
                f"User: {h['user']}\nChatbot: {h['chatbot']}"
                for h in conversation_history[-10:]
            )

            combined_prompt = (
                base_prompt
                + "\n\n### Original Conversation:\n" + conv_text
                + "\n\n### GPT Feedback:\n"    + gpt_summary
                + "\n\n### Llama Feedback:\n"  + llama_summary
            )
            seeker_query = seeker(base_prompt, history_text, temperature)

            start = datetime.now()
            try:
                chatbot_response = get_gpt_response(combined_prompt + seeker_query)
            except Exception as e:
                print(f"[ERROR❌] get_gpt_response failed for {conv_id}: {e}")
                continue
            response_time = (datetime.now() - start).total_seconds()
            conversation_history.append({
                "user":    seeker_query,
                "chatbot": chatbot_response
            })

            with open(convo_file, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                writer.writerow([
                    seeker_query,
                    chatbot_response,
                    round(response_time, 2),
                    temperature,
                ])

        print(f"[OK✅] Generated improved convo for {conv_id}")


def generate_criteria_convs():
    """
    For each persona and criterion, simulate new trajectories
    for conversations that scored below the percentile threshold,
    logging all outputs into a single directory.
    """
    # 1) get low-rated conversation IDs per persona/criterion
    low_dict = get_low_criteria_rating_ids()

    # 2) load each persona's DataFrame
    persona_paths = {
        "User":     os.path.join(GPT_CRITERIA_RATINGS, "user.csv"),
        "Observer": os.path.join(GPT_CRITERIA_RATINGS, "observer.csv"),
        "Self":     os.path.join(GPT_CRITERIA_RATINGS, "self.csv"),
    }
    persona_dfs = {p: pd.read_csv(path) for p, path in persona_paths.items()}

    # 3) ensure single output directory exists
    os.makedirs(GPT_CRITERIA_CONVO_DIR, exist_ok=True)

    # 4) iterate personas and criteria
    for persona, crit_map in low_dict.items():
        df_persona = persona_dfs[persona]
        for criterion, conv_ids in crit_map.items():
            if not conv_ids:
                continue

            for conv_id in conv_ids:
                # lookup rating
                row = df_persona[df_persona["Conversation_Id"] == conv_id]
                if row.empty:
                    print(f"[WARN⚠️] {persona}/{criterion}: no data for ID={conv_id}")
                    continue
                rating_value = row.iloc[0][criterion]

                # read original conversation
                conv_path = os.path.join(PREV_CONV_DIR, f"trajectory{conv_id}.csv")
                if not os.path.exists(conv_path):
                    print(f"[WARN⚠️] Missing {conv_path}")
                    continue
                conv_text = open(conv_path, encoding="utf8").read().strip()

                # generate feedback summaries
                try:
                    gpt_sum = gpt_summalyzer(conv_text, rating_value, criterion)
                    llama_sum = llama_summalyzer(conv_text, rating_value, criterion)
                except Exception as e:
                    print(f"[ERROR❌] Summaries failed {persona}/{criterion}/{conv_id}: {e}")
                    continue

                # load base prompt
                prompt_path = os.path.join(PROMPT_DIR, f"prompt{conv_id}.txt")
                if not os.path.exists(prompt_path):
                    print(f"[WARN⚠️] Missing prompt {prompt_path}")
                    continue
                base_prompt = open(prompt_path, encoding="utf8").read().strip()

                # prepare CSV path in single directory
                file_name = f"conv_{conv_id}_{persona}_{criterion}.csv"
                convo_csv = os.path.join(GPT_CRITERIA_CONVO_DIR, file_name)
                initialize_convo_csv(convo_csv)

                history = []
                # simulate conversation turns
                for _ in range(NUM_QUERIES):
                    temp = round(random.uniform(0.5, 1.0), 2)
                    hist_text = "\n".join(
                        f"User: {h['user']}\nChatbot: {h['chatbot']}"
                        for h in history[-10:]
                    )

                    combined = (
                        base_prompt
                        + "\n\n### Previous Conversation:\n" + conv_text
                        + "\n\n### GPT Feedback for “" + criterion + "”:\n" + gpt_sum
                        + "\n\n### Llama Feedback for “" + criterion + "”:\n" + llama_sum
                    )

                    seeker_query = seeker(combined, hist_text, temp)
                    start = datetime.now()
                    try:
                        bot_r = get_gpt_response(seeker_query)
                    except Exception as e:
                        bot_r = f"[ERROR❌] {e}"
                    rt = (datetime.now() - start).total_seconds()

                    history.append({"user": seeker_query, "chatbot": bot_r})

                    # append to CSV
                    with open(convo_csv, mode="a", newline="", encoding="utf8") as f:
                        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                        writer.writerow([seeker_query, bot_r, round(rt,2), temp])

                print(f"[OK✅] Generated trajectories for conv {conv_id} ({persona}/{criterion})")



if __name__ == '__main__':
    # generate_criteria_convs()
    pass