import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OpenAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OpenAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=OpenAI_API_KEY)


SELF_ASSESSMENT_PROMPT = """
You are the chatbot who just completed this conversation.

Now reflect on your performance as a helper and communicator.

Rate yourself based on:
- How clearly you explained things
- Whether you stayed on topic
- If your tone was appropriate and supportive
- Whether you answered the user's questions effectively
- How well you adapted to the user's language level
- How concise and digestible your responses were
- Whether you avoided technical jargon or overwhelming information
- Whether you repeated yourself or contradicted earlier answers
- How inclusive and respectful your responses were

Score your overall performance in this conversation **from 1 to 10**.

**Only return a single floating-point number between 1 and 10. No explanation.**
**❗❗Your response would be thrown out if you return anything other than a single floating point number❗❗**""
"""


SELF_PER_TURN_PROMPT = """
You are the chatbot reviewing your own response to the user in this specific interaction.

Rate your performance for this message based on:
- How well you understood and answered the user’s exact question
- Whether your explanation was clear, simple, and easy to understand
- If you used short sentences and avoided complex words or public health jargon
- Whether your tone was supportive, inclusive, and free of judgment
- How well you followed the user’s language level and communication needs
- Whether you stayed focused and didn’t over-explain or go off topic

Score this single chatbot response on a scale from 1 to 10.

**Only return a single floating-point number between 1 and 10. No explanation.**
**❗❗Your response would be thrown out if you return anything other than a single floating point number❗❗**""
"""


USER_ASSESSMENT_PROMPT = """
You are the user who just had this conversation with the chatbot.

You are asked to rate your **overall satisfaction** with the interaction based on:
- How helpful and useful the chatbot was
- Whether your questions were answered clearly and respectfully
- If the responses were easy for you to read and understand
- Whether you felt supported, not judged, and able to ask anything
- Whether the chatbot made you feel more informed, safer, or more confident
- If anything felt confusing, unhelpful, or off-topic

Rate your satisfaction **on a scale from 1 to 10**, with 10 meaning very satisfied and 1 meaning very dissatisfied.

**Only return a single floating-point number between 1 and 10. No explanation.**
**❗❗Your response would be thrown out if you return anything other than a single floating point number❗❗**""
"""


USER_PER_TURN_PROMPT = """
You are the user who asked this question and received the chatbot’s answer.

Rate your satisfaction with this single chatbot response based on:
- Whether your question was fully and clearly answered
- How easy the response was for you to read and understand
- If the tone felt respectful, helpful, and non-judgmental
- Whether the answer made you feel better informed or reassured
- If anything was confusing, too complex, or didn’t make sense to you

Rate your satisfaction for this turn only, from 1 to 10.

**Only return a single floating-point number between 1 and 10. No explanation.**
**❗❗Your response would be thrown out if you return anything other than a single floating point number❗❗**""
"""


THIRD_PARTY_ASSESSMENT_PROMPT = """
You are a third-party evaluator observing a full conversation between a user and an HIV prevention chatbot.

Your job is to analyze the **quality, clarity, consistency, and helpfulness** of the chatbot's responses.

Evaluate based on:
- Whether the chatbot answered each question clearly, accurately, and directly
- If the responses were free of unnecessary jargon and matched the user’s language level
- How consistent the chatbot was when handling similar questions or topics
- Whether the chatbot avoided contradictions or repeating itself
- How well the chatbot adapted to changes in the user’s tone or focus
- Whether the overall tone was inclusive, supportive, and aligned with health literacy principles
- How well the conversation flowed and stayed focused on HIV prevention or PrEP

Rate the **overall performance of the chatbot in this conversation** on a scale from 1 to 10.

**Only return a single floating-point number between 1 and 10. No explanation.**
**❗❗Your response would be thrown out if you return anything other than a single floating point number❗❗**""
"""


THIRD_PARTY_PER_TURN_PROMPT = """
You are a third-party expert reviewing a single user-chatbot interaction from a conversation about HIV prevention and PrEP.

Your goal is to rate how well the chatbot responded to the user’s message in this turn.

Evaluate based on:
- Clarity and simplicity of the chatbot’s response
- Relevance, accuracy, and helpfulness of the information provided
- Whether the chatbot avoided technical jargon and complex language
- Appropriateness of tone (supportive, respectful, inclusive)
- Whether the chatbot answered the user’s specific question without straying off-topic
- If the response used short sentences and accessible words

Rate the quality of this single Q&A turn from 1 to 10.

**Only return a single floating-point number between 1 and 10. No explanation.**
**❗❗Your response would be thrown out if you return anything other than a single floating point number❗❗**""
"""

def user_criteria_prompt(criteria):
    return f"""
        You are the user who just had a conversation with a chatbot about HIV prevention.

        Please rate the chatbot **based only on the following criterion**:  
        **{criteria}**

        Use a scale from 1 to 10:
        - 10 means excellent
        - 1 means very poor

        **Only return a single floating-point number between 1 and 10. No explanation.**
        """

def self_criteria_prompt(criteria):
    return f"""
        You are the chatbot that just completed this conversation with a user.

        Reflect on your performance **based only on the following criterion**:  
        **{criteria}**

        Rate yourself on a scale from 1 to 10, where:
        - 10 means you did perfectly
        - 1 means you performed poorly

        **Only return a single floating-point number between 1 and 10. No explanation.**
        **❗❗Your response would be thrown out if you return anything other than a single floating point number❗❗**""
        """

def third_party_criteria_prompt(criteria):
    return f"""
        You are a third-party evaluator analyzing a conversation between a user and a chatbot.

        Evaluate the chatbot's performance **based only on the following criterion**:  
        **{criteria}**

        Rate the performance on a scale from 1 to 10:
        - 10 = excellent
        - 1 = very poor

        **Only return a single floating-point number between 1 and 10. No explanation.**
        **❗❗Your response would be thrown out if you return anything other than a single floating point number❗❗**""
        """


def get_gpt_overall_rating(prompt, conversation):

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Here is the full conversation:\n\n{conversation}\n\nPlease give your rating."}
    ]
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens = 4,
            temperature=0.2
        )

        rating = response.choices[0].message.content
        return rating
    except Exception as e:
        return f"GPT experienced an internal error: {str(e)}"
    
