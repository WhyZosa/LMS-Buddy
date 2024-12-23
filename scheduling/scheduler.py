# my_bot/scheduling/scheduler.py
import schedule
import time
from datetime import datetime, timedelta
import schedule
import time
from storage.models import (
    Deadline,
    Subject,
    Session
)



def send_notifications(bot, user_data):
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

def remind_sop_dates(bot, user_data):
    today = datetime.now().date()
    sop_periods = [
        (datetime(2024, 10, 8).date(), datetime(2024, 10, 24).date()),
        (datetime(2024, 11, 29).date(), datetime(2024, 12, 19).date()),
        (datetime(2025, 2, 17).date(), datetime(2025, 3, 3).date()),
        (datetime(2025, 5, 30).date(), datetime(2025, 6, 19).date())
    ]
    for start, end in sop_periods:
        if start <= today <= end:
            for chat_id in user_data.keys():
                bot.send_message(chat_id, "СОП в процессе! Не забудьте выполнить все задания.")

from sqlalchemy.orm import joinedload

def send_deadline_reminders(bot):
    """
    Проверяет дедлайны и отправляет напоминания за 3 дня и за 1 день.
    """
    today = datetime.now().date()
    session = Session()

    deadlines = session.query(Deadline).options(
        joinedload(Deadline.subject).joinedload(Subject.user)
    ).all()

    for deadline in deadlines:
        due_date = datetime.strptime(deadline.due_date, "%Y-%m-%d").date()
        days_left = (due_date - today).days

        if days_left == 3:
            bot.send_message(
                deadline.subject.user.telegram_id,
                f"Напоминание: через 3 дня дедлайн '{deadline.name}' для предмета '{deadline.subject.name}'."
            )
        elif days_left == 1:
            bot.send_message(
                deadline.subject.user.telegram_id,
                f"Напоминание: завтра дедлайн '{deadline.name}' для предмета '{deadline.subject.name}'."
            )
    session.close()


