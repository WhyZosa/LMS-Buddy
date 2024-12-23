from telebot import TeleBot
from datetime import datetime


from storage.models import get_subjects_by_user, get_deadlines_by_subject, get_all_reminders_by_user



def register_remind_handlers(bot: TeleBot):
    """
    Attaches reminders-related handlers to the bot.
    """
    @bot.message_handler(func=lambda message: message.text == "Список напоминаний")
    def handle_show_subjects_with_deadlines(message):
        """
        Показывает список всех предметов и их дедлайнов для пользователя.
        """
        telegram_id = message.chat.id
        subjects = get_subjects_by_user(telegram_id)

        if not subjects:
            bot.send_message(telegram_id, "У вас пока нет добавленных предметов и дедлайнов.")
            return

        response = "Ваши предметы и дедлайны:\n\n"
        for subject in subjects:
            response += f"📚 {subject.name}\n"
            deadlines = get_deadlines_by_subject(subject.id)
            if deadlines:
                for deadline in deadlines:
                    due_date = datetime.strptime(deadline.due_date, "%Y-%m-%d").strftime("%d.%m.%Y")
                    response += f"   🔸 {deadline.name} (Тип: {deadline.deadline_type.value}, Дата: {due_date})\n"
            else:
                response += "   🔹 Нет дедлайнов\n"
            response += "\n"

        bot.send_message(telegram_id, response)




    @bot.message_handler(func=lambda message: message.text == "Все напоминания")
    def handle_show_all_reminders(message):
        """
        Показывает все дедлайны пользователя, сгруппированные по предметам,
        а также ближайшую дату напоминания о СОПе.
        """
        telegram_id = message.chat.id
        response = "Ваши напоминания:\n\n"
        subjects = get_subjects_by_user(telegram_id)
        if not subjects:
            response += "У вас пока нет добавленных предметов и дедлайнов.\n\n"
        else:
            response += "Ваши предметы и дедлайны:\n\n"
            for subject in subjects:
                response += f"📚 {subject.name}\n"
                deadlines = get_deadlines_by_subject(subject.id)
                if deadlines:
                    for deadline in deadlines:
                        due_date = datetime.strptime(deadline.due_date, "%Y-%m-%d").strftime("%d.%m.%Y")
                        response += f"   🔸 {deadline.name} (Тип: {deadline.deadline_type.value}, Дата: {due_date})\n"
                else:
                    response += "   🔹 Нет дедлайнов\n"
                response += "\n"
        response += "Ближайшая дата напоминания о СОПе:\n"

        today = datetime.now().date()
        sop_periods = [
            (datetime(2024, 10, 8).date(), datetime(2024, 10, 24).date()),
            (datetime(2024, 11, 29).date(), datetime(2024, 12, 19).date()),
            (datetime(2025, 2, 17).date(), datetime(2025, 3, 3).date()),
            (datetime(2025, 5, 30).date(), datetime(2025, 6, 19).date())
        ]

        upcoming_sop = None
        for start, end in sop_periods:
            if today <= end:
                upcoming_sop = (start, end)
                break

        if upcoming_sop:
            start, end = upcoming_sop
            response += f"   🔹 С {start.strftime('%d.%m.%Y')} по {end.strftime('%d.%m.%Y')}\n"
        else:
            response += "   🔹 Нет предстоящих СОПов.\n"

        bot.send_message(telegram_id, response)
    def handle_show_reminders(message):
        """
        Показывает список всех напоминаний пользователя.
        """
        telegram_id = message.chat.id
        reminders = get_all_reminders_by_user(telegram_id)

        if not reminders:
            bot.send_message(telegram_id, "У вас пока нет добавленных предметов или дедлайнов.")
            return

        response = "Ваши напоминания:\n\n" + "\n\n".join(reminders)
        bot.send_message(telegram_id, response)