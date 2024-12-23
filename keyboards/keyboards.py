from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def main_menu():
    """
    Главное меню бота (ReplyKeyboard)
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("Предметы и дедлайны"),
        KeyboardButton("Уведомление об учебных парах"),
        KeyboardButton("Все напоминания"),
        KeyboardButton("F.A.Q. для студентов"),
        KeyboardButton("Уезжаю на каникулы")
    )
    return markup

def subjects_keyboard(subjects):
    """
    Инлайн-клавиатура с предметами.
    """
    markup = InlineKeyboardMarkup()
    for subject in subjects:
        markup.add(InlineKeyboardButton(subject.name, callback_data=f"subject_{subject.id}"))
    markup.add(InlineKeyboardButton("Добавить предмет", callback_data="add_subject"))
    return markup

def deadlines_keyboard(subject_id, deadlines):
    """
    Инлайн-клавиатура с дедлайнами для предмета.
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
