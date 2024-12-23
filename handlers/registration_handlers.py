from telebot import TeleBot
from datetime import datetime


from storage.models import create_user, is_user_registered
from keyboards.keyboards import main_menu

def register_registration_handlers(bot: TeleBot, user_data: dict):
    """
    Attaches registration-related handlers to the bot.
    """

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        """
        Handler for the /start command.
        """
        telegram_id = message.chat.id
        if is_user_registered(telegram_id):
            bot.send_message(telegram_id, "Добро пожаловать обратно в LMS-Buddy!", reply_markup=main_menu())
        else:
            bot.send_message(
                telegram_id,
                "Добро пожаловать в LMS-Buddy! Давайте начнём с регистрации.\nВведите ваше имя:"
            )
            user_data[telegram_id] = {}
            bot.register_next_step_handler(message, ask_surname)

    def ask_surname(message):
        """
        Запрашивает фамилию пользователя.
        """
        telegram_id = message.chat.id
        user_data[telegram_id]['name'] = message.text
        bot.send_message(telegram_id, "Введите вашу фамилию:")
        bot.register_next_step_handler(message, ask_family_name)

    def ask_family_name(message):
        """
        Запрашивает отчество пользователя.
        """
        telegram_id = message.chat.id
        user_data[telegram_id]['surname'] = message.text
        bot.send_message(telegram_id, "Введите ваше отчество:")
        bot.register_next_step_handler(message, finish_registration)

    def finish_registration(message):
        """
        Завершает процесс регистрации и сохраняет данные пользователя в базе.
        """
        telegram_id = message.chat.id
        user_data[telegram_id]['family_name'] = message.text

        create_user(
            telegram_id=telegram_id,
            name=user_data[telegram_id]['name'],
            surname=user_data[telegram_id]['surname'],
            family_name=user_data[telegram_id]['family_name']
        )
        bot.send_message(
            telegram_id,
            "Регистрация завершена! Чем я могу вам помочь?",
            reply_markup=main_menu()
        )
