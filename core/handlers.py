from telebot.types import Message
from core.keyboards import main_menu
from storage.models import create_user, add_subject

def handle_start(bot, message: Message):
    bot.send_message(message.chat.id, "Добро пожаловать! Введите ваше имя:")
    bot.register_next_step_handler(message, lambda msg: ask_surname(bot, msg))

def ask_surname(bot, message: Message):
    user_data = {"name": message.text}
    bot.send_message(message.chat.id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, lambda msg: finish_registration(bot, msg, user_data))

def finish_registration(bot, message: Message, user_data):
    user_data["surname"] = message.text
    user_id = create_user(user_data["name"], user_data["surname"], "Фамилия")
    bot.send_message(message.chat.id, f"Регистрация завершена! Ваш ID: {user_id}", reply_markup=main_menu())
