import os
import logging
from telegram.ext import Updater, CommandHandler, dispatcher
from telegram.update import Update

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


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
    pass


def initialize_bot():
    TOKEN = os.environ["TELEGRAM_TOKEN"]

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    status_handler = CommandHandler("status", status)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(status_handler)

    return updater


def chat():
    updater = initialize_bot()
    updater.start_polling()
    updater.idle()


def alert(user_chat_id, message):
    updater = initialize_bot()
    updater.bot.send_message(chat_id=user_chat_id, text=message)

    updater.start_polling()
    updater.idle()


# if __name__ == "__main__":
#     chat()
