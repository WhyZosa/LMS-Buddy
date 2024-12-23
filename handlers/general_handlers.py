from telebot import TeleBot
from datetime import datetime


from keyboards.keyboards import main_menu
from .foreign_status_handlers import register_foreign_status_handlers
from .reminder_handlers import register_remind_handlers


def register_general_handlers(bot: TeleBot, user_data: dict):
    @bot.message_handler(func=lambda message: True)
    def menu_handler(message):
        chat_id = message.chat.id

        handle_foreign_status = register_foreign_status_handlers['handle_foreign_status'](bot)
        handle_show_reminders = register_remind_handlers['handle_show_reminders'](bot)

        if message.text == "Список напоминаний":
            handle_show_reminders(message)

        elif message.text == "Уезжаю на каникулы":
            bot.send_message(chat_id, "Вы уезжаете на каникулы? Ответьте 'Да' или 'Нет'.")
            bot.register_next_step_handler(message, handle_foreign_status)

        elif message.text == "Назад":
            bot.send_message(chat_id, "Возвращаемся в главное меню.", reply_markup=main_menu())
            user_data[chat_id]['state'] = None

        else:
            bot.send_message(chat_id, f"Функционал '{message.text}' пока в разработке.", reply_markup=main_menu())

    @bot.message_handler(func=lambda message: message.text == "F.A.Q. для студентов")
    def handle_faq(message):
        """
        Показывает гайд по использованию бота.
        """
        faq_text = (
            "📘 *F.A.Q. для студентов*\n\n"
            "Добро пожаловать в *LMS-Buddy*! Вот что я умею и как вы можете использовать мои функции:\n\n"
            "1️⃣ *Моя напоминалка*\n"
            "   - Добавляйте предметы и дедлайны.\n"
            "   - Управляйте дедлайнами: просматривайте их и отмечайте как выполненные.\n"
            "   - Команда 'Все напоминания' покажет список всех ваших предметов и дедлайнов.\n\n"
            "2️⃣ *Уведомление об учебных парах*\n"
            "   - Получайте расписание ваших пар.\n"
            "   - Укажите предметы, и я напомню вам о них.\n\n"
            "3️⃣ *Уезжаю на каникулы*\n"
            "   - Сообщите мне, если вы уезжаете на каникулы.\n"
            "   - Укажите дату возвращения, чтобы я мог напомнить вам о регистрации.\n\n"
            "4️⃣ *Все напоминания*\n"
            "   - Получите полный список ваших дедлайнов и ближайшую дату СОПа.\n\n"
            "5️⃣ *F.A.Q. для студентов*\n"
            "   - Читайте этот гайд, чтобы узнать, как пользоваться ботом.\n\n"
            "Если у вас есть вопросы или предложения, напишите в учебный офис. Я всегда готов помочь! 😊"
        )
        bot.send_message(message.chat.id, faq_text, parse_mode="Markdown")
