import openai
import logging

from typing import Optional
from database import db

async def completion(chat_history, prompt_id, model) -> str: # chat_history = [user, ai, user, ai, ..., user]
    assert len(chat_history) % 2 == 1
    messages=[{"role": "system", "content": db.prompt(prompt_id)}]
    roles = ["user", "assistant"]
    role_id = 0
    for msg in chat_history:
        messages.append({"role": roles[role_id], "content": msg})
        role_id = 1 - role_id
    logging.info('Request: %s', messages)
    response = await openai.ChatCompletion.acreate(model=model, messages=messages)
    logging.info('Response: %s', response)
    if response['choices'][0]['message']['role'] != 'assistant':
        return
    return response['choices'][0]['message']['content']

def construct_chat_history(chat_id: int, msg_id: int, db) -> tuple[str, int]:
    prompt_id = None
    messages = []
    should_be_bot = False
    while True:
        key = repr((chat_id, msg_id))
        if not db.contains(key):
            logging.error('History message not found')
            return None, None
        is_bot, text, reply_id, prompt_id = db[key]
        if is_bot != should_be_bot:
            logging.error('Role does not match')
            return None, None
        messages.append(text)
        should_be_bot = not should_be_bot
        if reply_id is None:
            break
        msg_id = reply_id
    if len(messages) % 2 != 1:
        logging.error('First message not from user')
        return None, None
    return messages[::-1], prompt_id

async def reply_inner(text: str, prompt_id: int, chat_id: int, msg_id: int, reply_to_id: Optional[int], db, model: str) -> str:
    db[repr((chat_id, msg_id))] = (False, text, reply_to_id, prompt_id)
    chat_history, prompt_id = construct_chat_history(chat_id, msg_id, db)
    if chat_history is None:
        return "这段对话记录我找不到了……你确定这是我们之前的对话吗？"

    try:
        return await completion(chat_history, prompt_id, model)
    except openai.OpenAIError as e:
        logging.exception('OpenAI Error: %s', e)
        return f'[!] OpenAI Error: {e}'
