import os
import logging
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, dispatcher
from telegram.update import Update

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = os.environ["TELEGRAM_TOKEN"]
PORT = int(os.environ.get("PORT", "8443"))
APP_NAME = os.environ["APP_NAME"]

msg_template = """
{0} <b>{1}</b> down <b>{2}</b>% {0}


📉 ${4}
🛍 <pre>{3}</pre>


🛒 <b>Shop now</b>: {5}
"""


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello!")
    print(update.effective_chat.id)
    # check if registered user


def status(update, context):
    # get user
    # check if existing user
    # get user data from server
    # display
    update.message.reply_text("Sorry, can't access status, yet.")


def setup():

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    status_handler = CommandHandler("status", status)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(status_handler)

    return updater


def chat():
    updater = setup()
    # updater.start_polling()
    # updater.idle()

    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{APP_NAME}.herokuapp.com/{TOKEN}",
    )
    updater.idle()


def alert(user_chat_id, data):
    updater = setup()

    msg = msg_template.format(
        "🚨",
        data["product_name"],
        str(int(data["variation"] * 100)),
        data["site"],
        str(data["price"]),
        data["url"],
    )

    # TODO: check if throws an error when user not found, or blocked.
    message = updater.bot.send_message(
        chat_id=user_chat_id,
        text=msg,
        parse_mode=ParseMode.HTML,
    )
    message.edit_text(msg, disable_web_page_preview=True, parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    chat()