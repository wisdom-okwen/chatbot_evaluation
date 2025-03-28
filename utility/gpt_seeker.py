import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPEN_AI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPEN_AI_API_KEY)

def seeker(txt, history, temperature):
    """Simulates a conversation by generating a response from OpenAI."""
    
    prompt = (
        f"{txt}\n\n"
        "⚠️ **IMPORTANT:** You MUST NOT repeat questions that have already been asked in the conversation history. ⚠️\n"
        "✅ Only ask NEW, relevant questions based on the previous discussion.\n"
        "❌ If a question has already been asked, DO NOT reword or rephrase it.\n"
        "✅ If you need clarification, ask SPECIFIC follow-up questions instead.\n"
        "🚨 If you repeat a question, it will be ignored, so carefully check the history first. 🚨\n\n"
        "**Conversation history:**\n"
        f"{history}\n\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt, "type": "text"}
        ],
        max_tokens=100,
        temperature=temperature
    )
    return response.choices[0].message.content.strip()


if __name__ == '__main__':
    temp = 0.7
    txt = "Start by asking basic questions hesitantly, avoiding direct terms related to sexual health." 
    print(seeker(txt, [], temp))