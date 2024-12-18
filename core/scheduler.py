import schedule
import time
from storage.models import get_notifications

def send_notifications(bot):
    notifications = get_notifications()
    for chat_id, message in notifications:
        bot.send_message(chat_id, message)

def start_scheduler(bot):
    schedule.every().day.at("08:00").do(send_notifications, bot=bot)
    while True:
        schedule.run_pending()
        time.sleep(1)
