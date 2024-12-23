# my_bot/main.py
import time
import schedule
from threading import Thread
import telebot

from configs.config import BOT_TOKEN
from scheduling.scheduler import send_notifications, remind_sop_dates, send_deadline_reminders
from handlers.registration_handlers import register_registration_handlers
from handlers.subject_deadline_handlers import register_subject_handlers
from handlers.general_handlers import register_general_handlers
from handlers.foreign_status_handlers import register_foreign_status_handlers
from handlers.reminder_handlers import register_remind_handlers

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}  # local dictionary for storing registration steps



from functools import partial

def schedule_notifications(bot):
    schedule.every().day.at("08:00").do(partial(send_notifications, bot, user_data))
    schedule.every().monday.at("10:00").do(partial(remind_sop_dates, bot, user_data))
    schedule.every().day.at("08:00").do(partial(send_deadline_reminders, bot))
    while True:
        schedule.run_pending()
        time.sleep(1)


def main():
    # Register handlers
    register_registration_handlers(bot, user_data)
    register_subject_handlers(bot)
    register_general_handlers(bot, user_data)
    register_foreign_status_handlers(bot)
    register_remind_handlers(bot)

    # Start scheduling in separate thread
    notification_thread = Thread(target=schedule_notifications, args=(bot,))
    notification_thread.daemon = True
    notification_thread.start()

    # Start bot
    bot.infinity_polling()

if __name__ == "__main__":
    main()
