import os
import openai
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)

from database import db
from handlers import (
    message_handler,
    add_to_whitelist_handler,
    del_from_whitelist_handler,
    get_whitelist_handler,
    ping,
    help,
    catgirl,
)

from config import admin_id, model
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
file_hanler = logging.FileHandler(__file__ + ".log")
console_handler = logging.StreamHandler()
logger.addHandler(file_hanler)
logger.addHandler(console_handler)

def main():
    whitelist = db.get('whitelist', set())
    if admin_id not in whitelist:
        whitelist.add(admin_id)
    db.clear()
    db['whitelist'] = whitelist

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.bot_data['admin_id'] = admin_id
    application.bot_data['model'] = model
    application.add_handlers([
        MessageHandler(filters.TEXT & ~(filters.COMMAND), message_handler, block=False),
        CommandHandler('add_whitelist', add_to_whitelist_handler, block=False),
        CommandHandler('del_whitelist', del_from_whitelist_handler, block=False),
        CommandHandler('get_whitelist', get_whitelist_handler, block=False),
        CommandHandler('ping', ping, block=False),
        CommandHandler('help', help, block=False),
        CommandHandler('start', help, block=False),
        CommandHandler('catgirl', catgirl, block=False),
    ])
    application.run_polling()

if __name__ == '__main__':
    main()