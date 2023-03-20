import logging
from telegram import Update
from telegram.ext import ContextTypes
from chat import reply_inner
from database import db
from validation import only_admin, only_private, only_whitelist, arg_num

@only_whitelist
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sender_id = update.message.from_user.id
    msg_id = update.message.message_id
    text = update.message.text

    logging.info('New message: chat=%r, sender=%r, id=%r, msg=%r', chat_id, sender_id, msg_id, text)
    
    reply_to_message = update.message.reply_to_message
    reply_to_id = None
    prompt_id = 0

    bot_id = (await context.bot.get_me()).id

    if reply_to_message is not None and update.message.reply_to_message.from_user.id == bot_id: # user reply to bot message
        reply_to_id = reply_to_message.message_id
    elif text.startswith('$'): # new message
        if text.startswith('$ '):
            text = text[2:]
        else:
            text = text[1:]
    else: # not reply or new message to bot
        if update.effective_chat.id == update.message.from_user.id: # if in private chat, send hint
            await update.message.reply_text("请用 $ 开头来创建一个新的对话，或者回复我的消息来继续已有的对话")
        return
    
    reply = await reply_inner(text, prompt_id, chat_id, msg_id, reply_to_id, db, context.bot_data['model'])
    message = await update.message.reply_text(reply)

    db[repr((chat_id, message.id))] = (True, reply, msg_id, prompt_id)
    logging.info('Reply message: chat=%r, sender=%r, id=%r, reply=%r', chat_id, sender_id, message.id, reply)

@only_whitelist
async def catgirl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    sender_id = update.message.from_user.id
    msg_id = update.message.message_id
    prompt_id = 1
    text = ' '.join(context.args)

    logging.info('New message: chat=%r, sender=%r, id=%r, msg=%r', chat_id, sender_id, msg_id, text)

    reply = await reply_inner(text, prompt_id, chat_id, msg_id, None, db, context.bot_data['model'])
    message = await update.message.reply_text(reply)

    db[repr((chat_id, message.id))] = (True, reply, msg_id, prompt_id)
    logging.info('Reply message: chat=%r, sender=%r, id=%r, reply=%r', chat_id, sender_id, message.id, reply)

@arg_num(0)
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"chat_id={update.effective_chat.id} user_id={update.message.from_user.id}")

@arg_num(0)
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("要开启一段新的对话，请以「$」开头并在后面追加你的问题，例如你可以提问：")
    await update.message.reply_text("$Telegram LLC 的创始人是谁？")
    await update.message.reply_text("要继续已有的对话并追加提问，请直接回复我的回答并提出你的问题。")

@arg_num(0, 1)
@only_admin
async def add_to_whitelist_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = update.effective_chat.id
    if len(context.args) == 1:
        try:
            target_id = int(context.args[0])
        except:
            await update.message.reply_text('Invalid chat id')
            return
    if db.is_whitelisted(target_id):
        await update.message.reply_text('Already in whitelist')
        return
    db.add_to_whitelist(target_id)
    await update.message.reply_text('Whitelist added')

@arg_num(0, 1)
@only_admin
async def del_from_whitelist_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = update.effective_chat.id
    if len(context.args) == 1:
        try:
            target_id = int(context.args[0])
        except:
            await update.message.reply_text('Invalid chat id')
            return
    if not db.is_whitelisted(target_id):
        await update.message.reply_text('Not in whitelist')
        return
    db.del_from_whitelist(target_id)
    await update.message.reply_text('Whitelist deleted')

@arg_num(0)
@only_admin
@only_private
async def get_whitelist_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(str(db.get_whitelist()))
