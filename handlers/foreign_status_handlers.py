from telebot import TeleBot
from datetime import datetime


from keyboards.keyboards import main_menu
from storage.models import  set_foreign_status

def register_foreign_status_handlers(bot: TeleBot):
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
