import configparser
import logging
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater, MessageHandler, Filters
import luhn

config = configparser.ConfigParser()
config.read("config.ini", encoding="UTF-8")

logger = logging.getLogger("bot_telegram")

TOKEN = config["TELEGRAM"]["Token"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

N_VISITORS = 0

def start(update: Update, context: CallbackContext):
    global N_VISITORS
    N_VISITORS += 1
    logger.info(f"N. visitors: {N_VISITORS}")
    text=("Hi, i'm bot who checks if a credit card number is valid using Luhn's algorithm"
    " (if you want to know more, [clicca qui](https://it.wikipedia.org/wiki/Formula_di_Luhn))\nPlease, use the command /check.\n\n")
    disclaimer = ("*DISCLAIMER*\nThis bot doesn't collect personal data.\n"
    "The data entered will be used only for the purposes of the bot (check the validity of the number)")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{text} {disclaimer}",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

def check(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Please, send me a credit card number to verify."
    )

def process_text(update: Update, context: CallbackContext):
    text=update.message.text.strip()
    if not text.isdigit():
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="The number set is incorrect. Please, try again."
        )
    else:
        checksum = check_ccn(text)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"The number sent is a {'valid' if checksum else 'invalid'} number."
        )

def check_ccn(text):
    """ Check numbers using Luhn's Algorithm """
    return luhn.verify(text)

def error(update, context):
    """ Log Errors caused by Updates. """
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("check", check))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), process_text))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
