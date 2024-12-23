import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from threading import Thread
from datetime import datetime, timedelta
import schedule
import time
from configs.config import BOT_TOKEN
from storage.models import (
    create_user,
    subject_already_exists,
    add_subject,
    get_subjects_by_user,
    set_foreign_status,
    get_all_reminders_by_user,
    delete_deadline,
    add_deadline,
    get_deadlines_by_subject,
    is_user_registered,
    DeadlineType,
    Deadline,
    Subject,
    Session
)

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

#
##
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("Предметы и дедлайны"),
        KeyboardButton("Уведомление об учебных парах"),
        KeyboardButton("Все напоминания"),
        KeyboardButton("F.A.Q. для студентов"),
        KeyboardButton("Уезжаю на каникулы")
    )
    return markup
##
#

#
##
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
##
#

#
##
def subjects_keyboard(subjects):
    """
    Создаёт клавиатуру с предметами.
    """
    markup = InlineKeyboardMarkup()
    for subject in subjects:
        markup.add(InlineKeyboardButton(subject.name, callback_data=f"subject_{subject.id}"))
    markup.add(InlineKeyboardButton("Добавить предмет", callback_data="add_subject"))
    return markup

def deadlines_keyboard(subject_id, deadlines):
    """
    Создаёт клавиатуру с дедлайнами для предмета.
    """
    markup = InlineKeyboardMarkup()
    for deadline in deadlines:
        markup.add(
            InlineKeyboardButton(
                f"{deadline.name} ({deadline.deadline_type.value})",
                callback_data=f"deadline_{deadline.id}"
            ),
            InlineKeyboardButton("Выполнен", callback_data=f"delete_{deadline.id}")
        )
    markup.add(InlineKeyboardButton("Добавить дедлайн", callback_data=f"add_deadline_{subject_id}"))
    markup.add(InlineKeyboardButton("Назад к предметам", callback_data="back_to_subjects"))
    return markup
##
#

#
##
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
        bot.send_message(telegram_id, "У вас пока нет добавленных предметов. Хотите добавить новый?", reply_markup=markup)
    else:
        bot.send_message(telegram_id, "Ваши предметы:", reply_markup=subjects_keyboard(subjects))
##
#

#
##
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

##
#

#
##
@bot.message_handler(func=lambda message: message.text == "Назад")
def handle_back_to_main_menu(message):
    """
    Возвращает пользователя в главное меню.
    """
    bot.send_message(message.chat.id, "Возвращаюсь в главное меню.", reply_markup=main_menu())
##
#

#
##
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
##
#

#
##
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

##
#

#
##
@bot.callback_query_handler(func=lambda call: call.data == "add_subject")
def handle_add_subject_callback(call):
    """
    Начинает процесс добавления предмета через инлайн-клавиатуру.
    """
    bot.send_message(call.message.chat.id, "Введите название предмета:")
    bot.register_next_step_handler(call.message, finish_add_subject)

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
##
#
    
#
##
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
    show_subjects_menu(call.message)
##
#

#
##
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
##
#

#
##
def notifications_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("Ввести предмет и дату"),
        KeyboardButton("Список напоминаний"),
        KeyboardButton("Назад")
    )
    return markup
##
#

#
##
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Хендлер для команды /start. Проверяет регистрацию пользователя и отправляет в меню или начинает регистрацию.
    """
    telegram_id = message.chat.id

    user_exists = is_user_registered(telegram_id)

    if user_exists:
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
##
#

#
##
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
##
#

#
##
@bot.message_handler(func=lambda message: True)
def menu_handler(message):
    chat_id = message.chat.id

    if message.text == "Моя напоминалка":
        bot.send_message(chat_id, "Выберите действие:", reply_markup=notifications_menu())
        user_data[chat_id] = {'state': 'notifications_menu'}

    elif message.text == "Список напоминаний":
        handle_show_reminders(message)

    elif message.text == "Ввести предмет и дату":
        bot.send_message(chat_id, "Введите название предмета:")
        user_data[chat_id]['state'] = 'enter_subject'

    elif user_data.get(chat_id, {}).get('state') == 'enter_subject':
        user_data[chat_id]['subject'] = message.text
        bot.send_message(chat_id, "Введите дату сдачи в формате DD.MM.YYYY:")
        user_data[chat_id]['state'] = 'enter_date'

    elif user_data.get(chat_id, {}).get('state') == 'enter_date':
        try:
            date = datetime.strptime(message.text, "%d.%m.%Y")
            user_data[chat_id]['date'] = date
            user_data[chat_id]['state'] = None
            add_subject(chat_id, user_data[chat_id]['subject'])
            bot.send_message(
                chat_id,
                f"Сохранено: предмет {user_data[chat_id]['subject']}, дата сдачи {date.strftime('%d.%m.%Y')}. Я напомню вам за неделю, за 3 дня, за 2 дня и за 1 день!",
                reply_markup=main_menu()
            )
        except ValueError:
            bot.send_message(chat_id, "Неверный формат даты. Попробуйте снова (формат DD.MM.YYYY).")

    elif message.text == "Уезжаю на каникулы":
        bot.send_message(chat_id, "Вы уезжаете на каникулы? Ответьте 'Да' или 'Нет'.")
        bot.register_next_step_handler(message, handle_foreign_status)

    elif message.text == "Назад":
        bot.send_message(chat_id, "Возвращаемся в главное меню.", reply_markup=main_menu())
        user_data[chat_id]['state'] = None

    else:
        bot.send_message(chat_id, f"Функционал '{message.text}' пока в разработке.", reply_markup=main_menu())
##
#
#
##
def handle_foreign_status(message):
    if message.text.lower() == "да":
        bot.send_message(message.chat.id, "Когда вы вернётесь? Укажите дату в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(message, lambda msg: save_return_date(msg, True))
    elif message.text.lower() == "нет":
        set_foreign_status(message.chat.id, is_foreign=False)
        bot.send_message(message.chat.id, "Отлично! Мы всегда рядом для помощи.", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "Ответьте 'Да' или 'Нет'.")
        bot.register_next_step_handler(message, handle_foreign_status)

def save_return_date(message, is_foreign):
    try:
        return_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        set_foreign_status(message.chat.id, is_foreign=is_foreign, return_date=return_date)
        bot.send_message(message.chat.id, f"Спасибо! Ждём вашего возвращения {return_date}.", reply_markup=main_menu())
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный формат даты. Попробуйте снова.")
        bot.register_next_step_handler(message, lambda msg: save_return_date(msg, is_foreign))
##
#

#
##
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

def remind_sop_dates():
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

def send_deadline_reminders():
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

def schedule_notifications():
    schedule.every().day.at("08:00").do(send_notifications)
    schedule.every().monday.at("10:00").do(remind_sop_dates)
    schedule.every().day.at("08:00").do(send_deadline_reminders)
    while True:
        schedule.run_pending()
        time.sleep(1)

##
#

if __name__ == "__main__":
    notification_thread = Thread(target=schedule_notifications)
    notification_thread.daemon = True
    notification_thread.start()

    bot.infinity_polling()
