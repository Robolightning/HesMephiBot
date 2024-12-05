import json
import os
import telebot
import logging
import asyncio
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaDocument
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка токена из файла
def load_token():
    with open('token.txt', 'r', encoding='utf-8') as file:
        return file.read().strip()

# Загрузка сообщения из JSON-файла
def load_message(file_name):
    with open(f'data/{file_name}', 'r', encoding='utf-8') as file:
        return json.load(file)

# Загрузка пользователей из файла
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r', encoding='utf-8') as file:
            return set(json.load(file))
    return set()

# Сохранение пользователей в файл
def save_users(users):
    with open('users.json', 'w', encoding='utf-8') as file:
        json.dump(list(users), file)

# Инициализация бота
bot = telebot.TeleBot(load_token(), parse_mode=None)

# Загрузка списка пользователей
users = load_users()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users.add(message.chat.id)  # Добавляем пользователя в список
    save_users(users)  # Сохраняем пользователей
    send_message(message.chat.id, "welcome_message.json")

# Отправка сообщения с кнопками и вложениями
def send_message(chat_id, file_name):
    try:
        msg = load_message(file_name)
        text = msg["text"]
        attachments = [a for a in msg.get("attachments", []) if a]  # Убираем None из вложений
        buttons = [
            [InlineKeyboardButton(btn_text, callback_data=key)]
            for btn_text, key in msg["buttons"].items()
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        # Если нет вложений
        if not attachments:
            bot.send_message(chat_id, text, reply_markup=keyboard)

        # Если одно вложение (документ или изображение)
        elif len(attachments) == 1:
            attachment = attachments[0]
            if os.path.exists(f'data/{attachment}'):
                with open(f'data/{attachment}', 'rb') as file:
                    if attachment.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        bot.send_photo(chat_id, file, caption=text, reply_markup=keyboard)
                    else:
                        bot.send_document(chat_id, file, caption=text, reply_markup=keyboard)

        # Если несколько документов
        elif all(attachment.endswith(('.pdf', '.docx', '.txt')) for attachment in attachments):
            bot.send_message(chat_id, text)  # Отправка текста отдельно
            media_group = [InputMediaDocument(open(f'data/{attachment}', 'rb')) for attachment in attachments if os.path.exists(f'data/{attachment}')]
            bot.send_media_group(chat_id, media_group)
            bot.send_message(chat_id, "ᅠ", reply_markup=keyboard)

        # Если несколько изображений
        elif all(attachment.endswith(('.jpg', '.jpeg', '.png', '.gif')) for attachment in attachments):
            bot.send_message(chat_id, text)  # Отправка текста отдельно
            media_group = [InputMediaPhoto(open(f'data/{attachment}', 'rb')) for attachment in attachments if os.path.exists(f'data/{attachment}')]
            bot.send_media_group(chat_id, media_group)
            bot.send_message(chat_id, "ᅠ", reply_markup=keyboard)

        # Если вложения разнородные или больше одного изображения/документа
        else:
            bot.send_message(chat_id, text)  # Отправка текста отдельно
            media_group = []
            for attachment in attachments:
                if os.path.exists(f'data/{attachment}'):
                    if attachment.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        media_group.append(InputMediaPhoto(open(f'data/{attachment}', 'rb')))
                    else:
                        bot.send_document(chat_id, open(f'data/{attachment}', 'rb'))
            if media_group:
                bot.send_media_group(chat_id, media_group)
            bot.send_message(chat_id, "ᅠ", reply_markup=keyboard)

    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def process_callback(call):
    try:
        send_message(call.message.chat.id, call.data)
        bot.answer_callback_query(call.id)
    except Exception as e:
        logging.error(f"Произошла ошибка при обработке запроса: {e}")

# Функция для проверки расписания и отправки сообщений
async def check_schedule():
    schedule_file = 'schedule.json'
    while True:
        current_time = datetime.now().strftime('%H:%M')
        schedule_data = read_schedule(schedule_file)

        for event in schedule_data['events']:
            if event['time'] == current_time:
                message_file = event['message_file']
                for user in users:
                    send_message(user, message_file)
        await asyncio.sleep(3600)  # Проверяем каждый час

# Функция для чтения расписания
def read_schedule(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# Функция для запуска асинхронной проверки расписания
def run_async_schedule():
    asyncio.run(check_schedule())

# Запуск бота и проверки расписания
if __name__ == '__main__':
    # Запускаем проверку расписания в отдельном потоке
    threading.Thread(target=run_async_schedule, daemon=True).start()
    
    # Запускаем бота
    bot.polling(none_stop=True)