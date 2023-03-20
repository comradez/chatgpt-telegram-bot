from telegram import Update
from telegram.ext import ContextTypes
from database import db

def arg_num(*valid_arg_num_set):
    def wrapper(func):
        async def decorated(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if len(context.args) not in valid_arg_num_set:
                await update.message.reply_text(f"Invalid arg number. Options are {valid_arg_num_set}.")
                return
            await func(update, context)
        return decorated
    return wrapper

def only_admin(func):
    async def new_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message.from_user.id != context.bot_data['admin_id']:
            await update.message.reply_text('Only admin can use this command')
            return
        await func(update, context)
    return new_func

def only_private(func):
    async def new_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != update.message.from_user.id:
            await update.message.reply_text('This command only works in private chat')
            return
        await func(update, context)
    return new_func

def only_whitelist(func):
    async def new_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not db.is_whitelisted(update.effective_chat.id):
            if update.effective_chat.id == update.message.from_user.id:
                await update.message.reply_text('This chat is not in whitelist')
            return
        await func(update, context)
    return new_func
