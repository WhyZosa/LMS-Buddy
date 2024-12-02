import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import schedule
import time
from threading import Thread
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

# Хранилище данных для пользователей
user_data = {}

# Главное меню
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Уведомление об учебных парах"))
    markup.add(KeyboardButton("Моя напоминалка"))
    markup.add(KeyboardButton("Поиск свободных аудиторий"))
    markup.add(KeyboardButton("F.A.Q. для студентов"))
    markup.add(KeyboardButton("Сбор справок"))
    markup.add(KeyboardButton("Подготовка к независимым экзаменам"))
    markup.add(KeyboardButton("Обратная связь с Учебным офисом"))
    return markup

# Меню для "Уведомления об учебных парах"
def notifications_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Ввести предмет и дату"))
    markup.add(KeyboardButton("Назад"))
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_data[message.chat.id] = {}
    bot.reply_to(message, "Привет! Я LMS-Buddy. Чем могу помочь?", reply_markup=main_menu())

# Обработка выбора из меню
@bot.message_handler(func=lambda message: True)
def menu_handler(message):
    chat_id = message.chat.id

    if message.text == "Моя напоминалка":
        bot.reply_to(message, "Выберите действие:", reply_markup=notifications_menu())
        user_data[chat_id]['state'] = 'notifications_menu'
    
    elif message.text == "Ввести предмет и дату":
        bot.reply_to(message, "Введите название предмета:")
        user_data[chat_id]['state'] = 'enter_subject'
    
    elif user_data.get(chat_id, {}).get('state') == 'enter_subject':
        user_data[chat_id]['subject'] = message.text
        bot.reply_to(message, "Введите дату сдачи в формате DD.MM.YYYY:")
        user_data[chat_id]['state'] = 'enter_date'
    
    elif user_data.get(chat_id, {}).get('state') == 'enter_date':
        try:
            date = datetime.strptime(message.text, "%d.%m.%Y")
            user_data[chat_id]['date'] = date
            user_data[chat_id]['state'] = None
            bot.reply_to(message, f"Сохранено: предмет {user_data[chat_id]['subject']}, дата сдачи {date.strftime('%d.%m.%Y')}. Я напомню вам за неделю, за 3 дня, за 2 дня и за 1 день!", reply_markup=main_menu())
        except ValueError:
            bot.reply_to(message, "Неверный формат даты. Попробуйте снова (формат DD.MM.YYYY).")

    elif message.text == "Назад":
        bot.reply_to(message, "Возвращаемся в главное меню.", reply_markup=main_menu())
        user_data[chat_id]['state'] = None
    
    else:
        # Для всех других функций — пока в разработке
        bot.reply_to(message, f"Функционал '{message.text}' пока в разработке.", reply_markup=main_menu())

# Логика отправки напоминаний
def send_notifications():
    today = datetime.now().date()
    for chat_id, data in user_data.items():
        if 'date' in data and 'subject' in data:
            exam_date = data['date'].date()

            if exam_date - timedelta(days=7) == today:
                bot.send_message(chat_id, f"Напоминание: Через неделю сдача предмета {data['subject']}.")
            elif exam_date - timedelta(days=3) == today:
                bot.send_message(chat_id, f"Напоминание: Через 3 дня сдача предмета {data['subject']}.")
            elif exam_date - timedelta(days=2) == today:
                bot.send_message(chat_id, f"Напоминание: Через 2 дня сдача предмета {data['subject']}.")
            elif exam_date - timedelta(days=1) == today:
                bot.send_message(chat_id, f"Напоминание: Завтра сдача предмета {data['subject']}.")
            elif exam_date == today:
                bot.send_message(chat_id, f"Сегодня сдача предмета {data['subject']}! Удачи!")

# Планировщик задач для отправки напоминаний
def schedule_notifications():
    schedule.every().day.at("08:00").do(send_notifications)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Запуск бота
if __name__ == "__main__":
    # Запуск планировщика в отдельном потоке
    notification_thread = Thread(target=schedule_notifications)
    notification_thread.daemon = True
    notification_thread.start()

    # Запуск бота
    bot.infinity_polling()
