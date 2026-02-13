import config
import time
import json

from langchain_groq import ChatGroq


with open(config.UTILS_DIR.joinpath('system_messages.json'), 'r') as f:
    sys_messages = json.load(f)


def set_ai_model(model: str = config.GROQ_LLAMA3_1_70B):
    llm = ChatGroq(
        model=model,
        groq_api_key=config.GROQ_API_KEY
    )
    if model == config.GROQ_LLAMA3_1_70B:
        settings = {
            "max_rpm": 30,
            "max_rpd": 14400,
            "max_tpm": 6000,
            "max_tpd": 200000
        }
    elif model == config.GROQ_LLAMA3_2_90B:
        settings = {
            "max_rpm": 30,
            "max_rpd": 7000,
            "max_tpm": 7000,
            "max_tpd": 500000
        }
    else:
        raise ValueError("[llm] Model not found.")
    limits = {
        "start_time": time.time(),
        "requests_made": 0,
        "tokens_used": 0
    }
    return llm, settings, limits


def generate_questions(llm, settings, limits):
    messages = [
        {
            "role": "system",
            "content": sys_messages["generate_questions"]
        }
    ]
    response = llm.invoke(messages)

    tokens_used = response.usage_metadata["total_tokens"]
    reached_limit, limits = check_limits(tokens=tokens_used, requests=1, settings=settings, limits=limits)
    if reached_limit:
        raise ValueError("[llm] Reached token or request limit.")

    questions_json = json.loads(response.content)
    questions_list = [questions_json['questions'][i]['question'] for i in range(len(questions_json['questions']))]

    return questions_list, limits


def evaluate_response(llm, settings, limits, question, user_response):
    feedback_messages = [
        {
            "role": "system",
            "content": sys_messages["evaluate_response"]
        },
        {
            "role": "user",
            "content": f"Question: {question}\nResponse: {user_response}\nIs my response correct? Give me feedback."
        }
    ]
    response = llm.invoke(feedback_messages)
    tokens_used = response.usage_metadata["total_tokens"]
    reached_limit, limits = check_limits(tokens=tokens_used, requests=1, settings=settings, limits=limits)

    is_correct_messages = [
        {
            "role": "system",
            "content": sys_messages["is_correct"]
        },
        {
            "role": "user",
            "content": f"User answer: {user_response}\nFeedback: {response.content}. Reply just with 'True' or 'False'."
        }
    ]
    correct_response = llm.invoke(is_correct_messages)
    print(f"Evaluation of the response: {correct_response.content}")
    if "true" in correct_response.content.lower():
        passed = True
    elif "false" in correct_response.content.lower():
        passed = False
    else:
        passed = None
    tokens_used = correct_response.usage_metadata["total_tokens"]
    reached_limit, limits = check_limits(tokens=tokens_used, requests=1, settings=settings, limits=limits)

    if reached_limit:
        raise ValueError("[llm] Reached token or request limit.")

    return response.content, limits, passed


def check_limits(requests, tokens, settings, limits) -> tuple[bool, dict]:
    limits["tokens_used"] += tokens
    limits["requests_made"] += requests
    current_time = time.time()
    elapsed_time = current_time - limits["start_time"]
    if elapsed_time < 60:  # Less than a minute since start
        rpm = limits["requests_made"]
    else:
        rpm = limits["requests_made"] / (elapsed_time / 60)

    if rpm >= settings["max_rpm"]:
        cooldown_time = round(60 - (elapsed_time % 60))
        time.sleep(cooldown_time)  # Sleep for the remaining time to stay within RPM limit
        return False, limits

    if limits["tokens_used"] >= (settings["max_tpd"] - 200):
        print(f"[llm]Token limit per day reached: {limits['tokens_used']} tokens.")
        return True, limits
    elif limits["requests_made"] >= (settings["max_rpd"] - 10):
        print(f"[llm]Request limit per day reached: {limits['requests_made']} requests.")
        return True, limits

    return False, limits