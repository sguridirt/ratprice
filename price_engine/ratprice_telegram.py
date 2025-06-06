import os

from loguru import logger
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    Defaults,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from database import (
    save_user,
    fetch_user,
    save_product,
    get_user_products,
    get_last_price,
    user_untrack_product,
)
from scrappers import REGISTERED_SCRAPPERS
from URLFilter import URLFilter
from message_templates import (
    notification_msg,
    product_status_msg,
    confirm_user_registration_msg,
    confirm_product_msg,
    confirm_product_untracking,
    current_products_msg,
)
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
    CHOOSE_UNTRACK_PRODUCT,
    UNTRACK_PRODUCT,
) = range(8)

url_filter = URLFilter()

ask_to_signup_keyboard = [
    [
        InlineKeyboardButton("No", callback_data="CANCEL"),
        InlineKeyboardButton("Yes!", callback_data="SIGNUP"),
    ]
]
ask_to_signup_markup = InlineKeyboardMarkup(ask_to_signup_keyboard)

confirm_keyboard = [
    [
        InlineKeyboardButton("Cancel", callback_data="cancel"),
        InlineKeyboardButton("Confirm", callback_data="confirm"),
    ]
]
confirm_keyboard_markup = InlineKeyboardMarkup(confirm_keyboard)


def start(update: Update, context: CallbackContext) -> int:
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
            text=f"I'm at your service.\nIf you want to see the status of your tracked products, send /status.\nIf you want to register a new product to track, use the /track command.",
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


def status(update: Update, context: CallbackContext) -> int:
    logger.info(
        f"> (i) {update.message.from_user['username']} ({update.effective_chat.id}) asked for his products status."
    )

    user = fetch_user(update.effective_chat.id)

    if user:
        products = get_user_products(user.id)

        for product in products:
            last_price, price_datetime = get_last_price(product.id)
            product_info = product.to_dict()

            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=product_status_msg.format(
                    product_info["name"],
                    last_price if last_price else 0,
                    price_datetime.strftime("%m/%d/%Y, %H:%M:%S (UTC)")
                    if price_datetime
                    else "never",
                    get_product_site(product_info["URL"]),
                ),
                parse_mode=ParseMode.HTML,
            )

        return -1

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, you need to be registered to access status.",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Do you want to register?",
            reply_markup=ask_to_signup_markup,
        )

        return SIGNUP_RESPONSE


def check_signup_response(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

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


def ask_for_username(update: Update, context: CallbackContext) -> int:
    username = update.message.text
    context.user_data["name"] = username

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=confirm_user_registration_msg.format(username),
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"OK?",
        reply_markup=confirm_keyboard_markup,
    )

    return SIGNUP_CONFIRMATION


def register_user(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    if query.data == "confirm":
        query.edit_message_text("OK ✅")

        save_user(update.effective_chat.id, context.user_data["name"])

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Your account has been created! 🎉",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="You can now procede to register your products with /track. After that, you'll just have to wait.",
        )
        return -1


def add_product(update: Update, context: CallbackContext) -> int:
    context.user_data["new_product"] = {}

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="➕  Lets register a new product!",
    )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Enter the product's *website link* \(eg\. https://www\.example\.com/\):",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    return REGISTER_URL


def register_product_url(update: Update, context: CallbackContext) -> int:
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
            text=f"I can't access this website's prices. The available websites are: {REGISTERED_SCRAPPERS}",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Please, enter a good product website link (eg. https://www.example.com/):",
        )
        return REGISTER_URL


def register_product_name_and_confirm(update: Update, context: CallbackContext) -> int:
    msg_text = update.message.text
    context.user_data["new_product"]["name"] = msg_text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=confirm_product_msg.format(
            context.user_data["new_product"]["name"],
            context.user_data["new_product"]["URL"],
        ),
        parse_mode=ParseMode.HTML,
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Confirm?",
        reply_markup=confirm_keyboard_markup,
    )

    return CONFIRM_NEW_PRODUCT


def register_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.delete_message()

    # TODO: display 'typing...'

    if query.data == "confirm":
        new_product_ref = save_product(
            name=context.user_data["new_product"]["name"],
            url=context.user_data["new_product"]["URL"],
            telegram_id=update.effective_chat.id,
        )
        context.user_data["new_product"] = {}

        if os.environ.get("MODE", "development") == "development":
            new_product_doc = new_product_ref.get()
            logger.info(
                f"> (i) Telegram: started tracking product ({new_product_doc.id}) for user {query.from_user['username']} ({query.from_user['id']})"
            )

        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Product added 🎉"
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Now I will track it and notify you any price drop!",
        )
        return -1
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚫 You canceled this product registration",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="To register a product, use /track."
        )


def untrack_product(update: Update, context: CallbackContext) -> int:
    logger.info(
        f"> (i) {update.message.from_user['username']} ({update.effective_chat.id}) asked to untrack a product."
    )

    user = fetch_user(update.effective_chat.id)

    if user:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="➖ Let's untrack a product."
        )

        products = [
            (product.id, product.to_dict()) for product in get_user_products(user.id)
        ]

        message = current_products_msg
        for i, product in enumerate(products):
            product_text = f"{i+1}. <b>{product[1]['name']}</b> ({product[1]['URL']})\n"
            message += product_text

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode=ParseMode.HTML,
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Which product do you want to untrack? Send the number before the product.",
        )

        context.user_data["products"] = products
        return CHOOSE_UNTRACK_PRODUCT

    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Sorry, you need to be registered to track and untrack products.",
        )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Do you want to register?",
            reply_markup=ask_to_signup_markup,
        )

        return SIGNUP_RESPONSE


def choose_untrack_product(update: Update, context: CallbackContext) -> int:
    msg_text = update.message.text

    if not msg_text.isdigit():
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="The message you sent was not a number. To re-do the (entire) request, use the command /untrack.",
        )
        return -1

    if int(msg_text) > len(context.user_data["products"]):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="The number you sent was not in the options. To re-do the (entire) request, use the command /untrack",
        )
        return -1

    product_chosen = context.user_data["products"][int(msg_text) - 1]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=confirm_product_untracking.format(
            product_chosen[1]["name"], product_chosen[1]["URL"]
        ),
        parse_mode=ParseMode.HTML,
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Confirm?",
        reply_markup=confirm_keyboard_markup,
    )

    context.user_data["product_chosen"] = product_chosen

    return UNTRACK_PRODUCT


def unlink_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    query.delete_message()

    if query.data == "confirm":
        product_chosen = context.user_data["product_chosen"]
        user = fetch_user(update.effective_chat.id)
        result = user_untrack_product(user.id, product_chosen[0])

        if result["success"]:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🎉 Succesfully deleted '{product_chosen[1]['name']}'.",
            )
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"Use the available commands if you want to do anything else.",
            )
            return -1
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🤔 Something failed, please try again. Use the /untrack command.",
            )

            return -1
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🚫 You canceled this product untracking",
        )
        return -1


def cancel(update: Update, context: CallbackContext) -> int:
    logger.info(
        f"> (i) {update.message.from_user['username']} has terminated the conversation."
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text="See you later! 😴")
    return -1


def error(update: Update, context: CallbackContext) -> int:
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="⚠️ Hey. I'm sorry to inform you that an error happened while I tried to handle your instructions. My developer will be notified.",
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🔄 You may want to try again to check if it was a temporary issue.",
    )

    logger.error(f'> (!) Telegram: update "{update}" caused error "{context.error}"')
    return -1


def setup():
    defaults = Defaults(disable_web_page_preview=True)
    updater = Updater(token=TOKEN, use_context=True, defaults=defaults)
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("status", status),
            CommandHandler("track", add_product),
            CommandHandler("untrack", untrack_product),
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
            CHOOSE_UNTRACK_PRODUCT: [
                MessageHandler(~Filters.command, choose_untrack_product)
            ],
            UNTRACK_PRODUCT: [CallbackQueryHandler(unlink_product)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(error)

    return updater


def chat():
    updater = setup()
    MODE = os.environ.get("MODE", "development")

    if MODE == "production":
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{APP_NAME}.herokuapp.com/{TOKEN}",
        )
    elif MODE == "development":
        updater.start_polling()

    updater.idle()


def choose_emoji(variation: int) -> str:
    emoji_scale = ["👀", "🙌", "🚨"]

    variation = abs(variation)

    if variation >= 0.4:
        return emoji_scale[2]
    elif variation >= 0.2:
        return emoji_scale[1]
    else:
        return emoji_scale[0]


def alert(user_chat_id: int, data: dict):

    updater = setup()

    msg = notification_msg.format(
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
