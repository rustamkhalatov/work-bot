import datetime
import sys

# Задаем разрешенные часы работы
allowed_hours = range(5, 24)  # Бот работает с 5 утра до 23:59

# Получаем текущее время
now = datetime.datetime.now()
current_hour = now.hour

# Проверяем, разрешено ли работать
if current_hour not in allowed_hours:
    print("Сейчас бот спит. Рабочие часы: с 5:00 до 23:59")
    sys.exit()

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Список админов
ADMINS = [1029030416]

# Список городов
CITIES = ['Ростов-на-Дону', 'Краснодар', 'Волгоград', 'Новороссийск', 'Пятигорск']

# Токен
TOKEN = '7987832917:AAEr2KQ2TMQRzgPEvB3G3pR1S3KkpXoWiBA'

# Словарь для хранения вакансий по городам
vacancies = {city: [] for city in CITIES}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[city] for city in CITIES]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Привет! Выберите город:', reply_markup=reply_markup)

async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = update.message.text
    if city not in CITIES:
        await update.message.reply_text('Пожалуйста, выберите город из списка.')
        return

    if vacancies[city]:
        jobs = "\n".join([f"{i+1}. {job}" for i, job in enumerate(vacancies[city])])
        await update.message.reply_text(f"Вакансии в {city}:\n{jobs}\n\nОтправьте свой номер телефона для отклика.",
                                        reply_markup=ReplyKeyboardMarkup(
                                            [[KeyboardButton("Отправить номер", request_contact=True)]],
                                            resize_keyboard=True
                                        ))
    else:
        await update.message.reply_text(
            "К сожалению, на данный момент вакансий нет. Следите за обновлениями!",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("Отправить номер", request_contact=True)]],
                resize_keyboard=True
            )
        )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contact = update.message.contact
    text = f"Новый отклик!\nИмя: {contact.first_name}\nТелефон: {contact.phone_number}"
    for admin_id in ADMINS:
        await context.bot.send_message(chat_id=admin_id, text=text)
    await update.message.reply_text('Спасибо! Ваши данные отправлены работодателю.')

async def add_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("У вас нет прав для добавления вакансий.")
        return

    try:
        city = context.args[0]
        vacancy_text = " ".join(context.args[1:])
        if city not in CITIES:
            await update.message.reply_text("Город не найден в списке.")
            return
        vacancies[city].append(vacancy_text)
        await update.message.reply_text(f"Вакансия добавлена в {city}!")
    except (IndexError, ValueError):
        await update.message.reply_text("Неверный формат. Используй: /addvacancy <Город> <Описание вакансии>")

async def delete_vacancy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("У вас нет прав для удаления вакансий.")
        return

    try:
        city = context.args[0]
        index = int(context.args[1]) - 1
        if city not in CITIES:
            await update.message.reply_text("Город не найден в списке.")
            return
        if 0 <= index < len(vacancies[city]):
            removed = vacancies[city].pop(index)
            await update.message.reply_text(f"Вакансия удалена: {removed}")
        else:
            await update.message.reply_text("Неверный номер вакансии.")
    except (IndexError, ValueError):
        await update.message.reply_text("Неверный формат. Используй: /deletevacancy <Город> <Номер вакансии>")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('addvacancy', add_vacancy))
    app.add_handler(CommandHandler('deletevacancy', delete_vacancy))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
