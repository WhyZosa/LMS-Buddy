import telebot
from config import BOT_TOKEN
from core.handlers import handle_start
from core.scheduler import start_scheduler
from threading import Thread

bot = telebot.TeleBot(BOT_TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    handle_start(bot, message)

if __name__ == "__main__":
    # Запуск планировщика в отдельном потоке
    scheduler_thread = Thread(target=start_scheduler, args=(bot,))
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Запуск бота
    bot.infinity_polling()
