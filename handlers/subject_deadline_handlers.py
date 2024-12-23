# my_bot/handlers/subject_handlers.py
from telebot import TeleBot
from datetime import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from storage.models import (
    subject_already_exists,
    add_subject,
    get_subjects_by_user,
    get_deadlines_by_subject,
    delete_deadline,
    add_deadline,
    DeadlineType,
)

from keyboards.keyboards import (
    main_menu,
    subjects_keyboard,
    deadlines_keyboard
)

def register_subject_handlers(bot: TeleBot):
    """
    Attaches subject/deadline-related handlers to the bot.
    """

    @bot.message_handler(func=lambda message: message.text == "Предметы и дедлайны")
    def handle_notifications_menu(message):
        """
        Отображает главное меню раздела 'Предметы и дедлайны'.
        """
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            KeyboardButton("Список предметов"),
            KeyboardButton("Добавить новый предмет"),
            KeyboardButton("Список напоминаний"),
            KeyboardButton("Назад")
        )
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

    @bot.message_handler(func=lambda message: message.text == "Список предметов")
    def show_subjects_menu(message):
        """
        Показывает список предметов пользователя.
        """
        telegram_id = message.chat.id
        subjects = get_subjects_by_user(telegram_id)
        if not subjects:
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("Добавить новый предмет"), KeyboardButton("Назад"))
            bot.send_message(
                telegram_id, 
                "У вас пока нет добавленных предметов. Хотите добавить новый?", 
                reply_markup=markup
            )
        else:
            bot.send_message(telegram_id, "Ваши предметы:", reply_markup=subjects_keyboard(subjects))

    @bot.message_handler(func=lambda message: message.text == "Добавить новый предмет")
    def handle_add_subject_message(message):
        """
        Начинает процесс добавления нового предмета через текстовое меню.
        """
        bot.send_message(message.chat.id, "Введите название нового предмета:")
        bot.register_next_step_handler(message, finish_add_subject)

    def finish_add_subject(message):
        """
        Завершает добавление предмета.
        """
        telegram_id = message.chat.id
        subject_name = message.text
        if subject_already_exists(telegram_id, subject_name):
            bot.send_message(message.chat.id, "Такой предмет уже существует")
            handle_add_subject_message(message)
            return
        add_subject(telegram_id, subject_name)
        bot.send_message(message.chat.id, f"Предмет '{subject_name}' успешно добавлен.")
        show_subjects_menu(message)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("subject_"))
    def show_deadlines(call):
        """
        Показывает список дедлайнов для выбранного предмета.
        """
        subject_id = int(call.data.split("_")[1])
        deadlines = get_deadlines_by_subject(subject_id)
        bot.edit_message_text(
            "Ваши дедлайны для предмета:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=deadlines_keyboard(subject_id, deadlines)
        )

    @bot.callback_query_handler(func=lambda call: call.data == "add_subject")
    def handle_add_subject_callback(call):
        """
        Начинает процесс добавления предмета через инлайн-клавиатуру.
        """
        bot.send_message(call.message.chat.id, "Введите название предмета:")
        bot.register_next_step_handler(call.message, finish_add_subject)

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_subjects")
    def handle_back_to_subjects(call):
        """
        Возвращает пользователя к списку предметов.
        """
        telegram_id = call.message.chat.id
        subjects = get_subjects_by_user(telegram_id)
        bot.edit_message_text(
            "Ваши предметы:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=subjects_keyboard(subjects)
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_deadline_"))
    def handle_add_deadline(call):
        """
        Начинает процесс добавления дедлайна для выбранного предмета.
        """
        subject_id = int(call.data.split("_")[2])
        bot.send_message(call.message.chat.id, "Введите название дедлайна:")
        bot.register_next_step_handler(call.message, lambda msg: ask_deadline_type(msg, subject_id))

    def ask_deadline_type(message, subject_id):
        """
        Запрашивает тип дедлайна.
        """
        deadline_name = message.text
        bot.send_message(
            message.chat.id,
            "Введите тип дедлайна (exam, homework, project):"
        )
        bot.register_next_step_handler(message, lambda msg: ask_deadline_date(msg, subject_id, deadline_name))

    def ask_deadline_date(message, subject_id, deadline_name):
        """
        Запрашивает дату дедлайна.
        """
        try:
            deadline_type = DeadlineType(message.text.lower())
            bot.send_message(
                message.chat.id,
                "Введите дату дедлайна в формате DD.MM.YYYY:"
            )
            bot.register_next_step_handler(message, lambda msg: finish_add_deadline(msg, subject_id, deadline_name, deadline_type))
        except ValueError:
            bot.send_message(message.chat.id, "Некорректный тип дедлайна. Попробуйте снова.")
            handle_add_deadline(message)

    def finish_add_deadline(message, subject_id, deadline_name, deadline_type):
        """
        Завершает добавление дедлайна.
        """
        try:
            due_date = datetime.strptime(message.text, "%d.%m.%Y").date()
            add_deadline(subject_id, deadline_name, deadline_type, due_date.strftime("%Y-%m-%d"))
            bot.send_message(message.chat.id, f"Дедлайн '{deadline_name}' успешно добавлен на {due_date.strftime('%d.%m.%Y')}. Я напомню вам за 3 дня и за 1 день до него!")
            show_subjects_menu(message)
        except ValueError:
            bot.send_message(message.chat.id, "Некорректный формат даты. Попробуйте снова.")
            handle_add_deadline(message)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
    def handle_delete_deadline(call):
        """
        Удаляет дедлайн по ID.
        """
        deadline_id = int(call.data.split("_")[1])
        delete_deadline(deadline_id)
        bot.answer_callback_query(call.id, "Дедлайн успешно удалён.")
        bot.edit_message_text(
            "Дедлайн удалён.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        # Refresh the subject menu
        telegram_id = call.message.chat.id
        subjects = get_subjects_by_user(telegram_id)
        bot.send_message(telegram_id, "Ваши предметы:", reply_markup=subjects_keyboard(subjects))

