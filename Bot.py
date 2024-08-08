import telebot
import schedule
import time
import logging
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot with your token
REMINDER_BOT_TOKEN = os.getenv('REMINDER_BOT_TOKEN')
bot = telebot.TeleBot(REMINDER_BOT_TOKEN)

# Path to the file where user IDs will be stored
USER_DATA_FILE = 'user_data.json'

# Reminder message
REMINDER_MESSAGE = """
📢 تذكير يومي لجمع العملات! 💰

لا تنسى الدخول إلى الرابط التالي لجمع العملات اليومية والاستفادة من الخصومات:

🔗 [جمع العملات](https://s.click.aliexpress.com/e/_DdwUZVd)

قم بجمع العملات الآن ولا تفوت الفرصة! 🏃‍♂️🏃‍♀️
"""

# Load user data
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save user data
def save_user_data(user_ids):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_ids, file)

# Add user to notification list
def add_user(user_id):
    user_ids = load_user_data()
    if user_id not in user_ids:
        user_ids.append(user_id)
        save_user_data(user_ids)
        logger.info(f"User {user_id} added to notification list.")
    else:
        logger.info(f"User {user_id} is already in the notification list.")

# Remove user from notification list
def remove_user(user_id):
    user_ids = load_user_data()
    if user_id in user_ids:
        user_ids.remove(user_id)
        save_user_data(user_ids)
        logger.info(f"User {user_id} removed from notification list.")
    else:
        logger.info(f"User {user_id} is not in the notification list.")

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    accept_button = InlineKeyboardButton("نعم", callback_data="accept")
    decline_button = InlineKeyboardButton("لا", callback_data="decline")
    markup.add(accept_button, decline_button)
    bot.send_message(message.chat.id, "مرحباً! هل ترغب في تلقي إشعارات لجمع العملات؟", reply_markup=markup)

# Handle callback queries from inline buttons
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "accept":
        add_user(call.message.chat.id)
        bot.send_message(call.message.chat.id, "تم تفعيل الإشعارات اليومية لجمع العملات! ستتلقى تذكيراً يومياً.")
    elif call.data == "decline":
        bot.send_message(call.message.chat.id, "تم إلغاء تفعيل الإشعارات لجمع العملات.")
    bot.answer_callback_query(call.id)

# Send reminder to all users in the notification list
def send_reminder():
    user_ids = load_user_data()
    for user_id in user_ids:
        try:
            bot.send_message(user_id, REMINDER_MESSAGE, parse_mode='Markdown')
            logger.info(f"Sent reminder to user {user_id} at {datetime.now()}")
        except Exception as e:
            logger.error(f"Error sending reminder to user {user_id}: {str(e)}")

# Schedule the reminder to be sent every day at a specific time
schedule.every().day.at("10:00").do(send_reminder)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logger.info("Starting reminder bot...")
    # Send reminder immediately for testing purposes
    send_reminder()
    bot.polling(none_stop=True)
    run_scheduler()
