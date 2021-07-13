import os

from loguru import logger
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    Defaults,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)

from database import save_user, fetch_user, save_product
from URLFilter import URLFilter
from scrappers import REGISTERED_SCRAPPERS
from utils import get_product_site

TOKEN = os.environ["TELEGRAM_TOKEN"]
PORT = int(os.environ.get("PORT", "8443"))
APP_NAME = os.environ["APP_NAME"]

(
    SIGNUP_RESPONSE,
    SIGNUP_NAME_REGISTRATION,
    SIGNUP_CONFIRMATION,
    REGISTER_URL,
    REGISTER_NAME,
    CONFIRM_NEW_PRODUCT,
) = range(6)

url_filter = URLFilter()

ask_to_signup_keyboard = [
    [
        InlineKeyboardButton("No", callback_data="CANCEL"),
        InlineKeyboardButton("Yes!", callback_data="SIGNUP"),
    ]
]
ask_to_signup_markup = InlineKeyboardMarkup(ask_to_signup_keyboard)

msg_template = """
{0} <b>{1}</b> down <b>{2}</b>% {0}


📉 ${4} (<s>${5}</s>)
🛍 <pre>{3}</pre>


🛒 <b>Shop now</b>: {6}
"""


def start(update, context):
    print("start")

    logger.info(
        f"> (i) Conversation started with {update.message.from_user['username']} ({update.effective_chat.id})"
    )

    user = fetch_user(update.effective_chat.id)

    if user:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Hello {user.to_dict()['name']} 👋",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"I'm at your service.\nIf you want to see the status of your tracked products, send /status.\nIf you want to register a new product to track, use the /add command.",
        )
        return -1
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hi! I am here to track the prices of internet products you tell me. I'll try to do my best to notify you when the price drops 📉. Enjoy!",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You are not registered 👀. To work properly and save your product prices, I need you to register",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Do you want to register?",
            reply_markup=ask_to_signup_markup,
        )

        return SIGNUP_RESPONSE


def status(update, context):
    logger.info(
        f"> (i) {update.message.from_user['username']} ({update.effective_chat.id}) asked for his products status."
    )

    user = fetch_user(update.effective_chat.id)

    if user:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Sorry {user.to_dict()['name']}, can't access status, yet.",
        )
        return -1

    # TODO: implement status
    update.message.reply_text("Sorry, can't access status, yet.")


def check_signup_response(update, context):
    query = update.callback_query

    if query.data == "SIGNUP":
        query.delete_message()
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sign up 📝 \nI'll only need your name. Please type how do you want to be called:",
        )
        return SIGNUP_NAME_REGISTRATION
    else:
        query.edit_message_text(
            text="Do you want to register? *NO*", parse_mode=ParseMode.MARKDOWN_V2
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I can't work if you don't signup ☹️. If you want to register, please use /start.",
        )
        return -1


def ask_for_username(update, context):
    username = update.message.text
    context.user_data["name"] = username

    confirm_keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data="cancel"),
            InlineKeyboardButton("Confirm", callback_data="confirm"),
        ]
    ]
    confirm_keyboard_markup = InlineKeyboardMarkup(confirm_keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Confirm your registration:\n username: {username}",
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"OK?",
        reply_markup=confirm_keyboard_markup,
    )

    return SIGNUP_CONFIRMATION


def register_user(update, context):
    query = update.callback_query

    if query.data == "confirm":
        query.edit_message_text("OK ✅")

        save_user(update.effective_chat.id, context.user_data["name"])

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Your account has been created! 🎉",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You can now procede to register your products with /add. After that, you'll just have to wait.",
        )
        return -1


def add_product(update, context):
    context.user_data["new_product"] = {}

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="➕  Lets register a new product!",
    )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Enter the Product website link (eg. https://www.example.com/):",
    )

    return REGISTER_URL


def register_product_url(update, context):
    msg_text = update.message.text
    site = get_product_site(msg_text)

    if site in REGISTERED_SCRAPPERS:
        context.user_data["new_product"]["URL"] = msg_text

        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Please, give it a name:"
        )

        return REGISTER_NAME
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"I can't access this website's prices, yet. The available websites are: {REGISTERED_SCRAPPERS}",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please, enter a good product website link (eg. https://www.example.com/):",
        )
        return REGISTER_URL


def register_product_name_and_confirm(update, context):
    msg_text = update.message.text
    context.user_data["new_product"]["name"] = msg_text

    confirm_keyboard = [
        [
            InlineKeyboardButton("Cancel", callback_data="cancel"),
            InlineKeyboardButton("Confirm", callback_data="confirm"),
        ]
    ]
    confirm_keyboard_markup = InlineKeyboardMarkup(confirm_keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Product:\nName: {context.user_data['new_product']['name']}\nURL: {context.user_data['new_product']['URL']}\n\nConfirm?",
        reply_markup=confirm_keyboard_markup,
    )

    return CONFIRM_NEW_PRODUCT


def register_product(update, context):
    query = update.callback_query

    if query.data == "confirm":
        query.edit_message_text(
            text=f"Product:\nName: {context.user_data['new_product']['name']}\nURL: {context.user_data['new_product']['URL']}",
        )
        save_product(
            name=context.user_data["new_product"]["name"],
            url=context.user_data["new_product"]["URL"],
            telegram_id=update.effective_chat.id,
        )
        context.user_data["new_product"] = {}

        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Product added 🎉"
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Now I will track it and notify you of any price drop!",
        )
        return -1
    else:
        query.edit_message_text(
            text=f"Product:\nName: {context.user_data['new_product']['name']}\nURL: {context.user_data['new_product']['URL']}",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚫 You canceled this product registration",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="To register a product, use /add."
        )


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="See you later! 😴")
    return -1


def setup():
    defaults = Defaults(disable_web_page_preview=True)
    updater = Updater(token=TOKEN, use_context=True, defaults=defaults)
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("status", status),
            CommandHandler("add", add_product),
        ],
        states={
            SIGNUP_RESPONSE: [CallbackQueryHandler(check_signup_response)],
            SIGNUP_NAME_REGISTRATION: [
                MessageHandler(~Filters.command, ask_for_username)
            ],
            SIGNUP_CONFIRMATION: [CallbackQueryHandler(register_user)],
            REGISTER_URL: [
                MessageHandler(~Filters.command & url_filter, register_product_url)
            ],
            REGISTER_NAME: [
                MessageHandler(Filters.all, register_product_name_and_confirm)
            ],
            CONFIRM_NEW_PRODUCT: [CallbackQueryHandler(register_product)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dispatcher.add_handler(conversation_handler)

    return updater


def chat():
    updater = setup()
    BOT_MODE = os.environ.get("BOT_MODE", "polling")

    if BOT_MODE == "webhook":
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{APP_NAME}.herokuapp.com/{TOKEN}",
        )
    elif BOT_MODE == "polling":
        updater.start_polling()

    updater.idle()


def choose_emoji(variation):
    emoji_scale = ["👀", "🙌", "🚨"]

    variation = abs(variation)

    if variation >= 0.4:
        return emoji_scale[2]
    elif variation >= 0.2:
        return emoji_scale[1]
    else:
        return emoji_scale[0]


def alert(user_chat_id, data):

    updater = setup()

    msg = msg_template.format(
        choose_emoji(data["variation"]),
        data["product_name"],
        str(int(data["variation"] * 100)),
        data["site"],
        str(data["price"]),
        str(data["old_price"]),
        data["url"],
    )

    updater.bot.send_message(
        chat_id=user_chat_id,
        text=msg,
        parse_mode=ParseMode.HTML,
    )

    logger.info("> (i) Notification sent")


if __name__ == "__main__":
    chat()
