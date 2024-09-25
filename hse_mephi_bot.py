import telebot
from telebot import types

botTimeWeb = telebot.TeleBot('7740540709:AAF4yOm_rRYknUF1Nmbacwc6Z44t4hl037c')

@botTimeWeb.message_handler(commands=['start'])
def startBot(message):
  first_mess = f"<b>{message.from_user.first_name} {message.from_user.last_name}</b>, привет!\nХочешь расскажу немного о ВИШ МИФИ?"
  markup = types.InlineKeyboardMarkup()
  button_yes = types.InlineKeyboardButton(text = 'Да', callback_data='yes')
  markup.add(button_yes)
  botTimeWeb.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)

@botTimeWeb.callback_query_handler(func=lambda call:True)
def response(function_call):
    if function_call.message:
        match function_call.data:
            case "yes":
                second_mess = "Скажи, что тебя интересует?"
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Поступление", callback_data='1'))
                markup.add(types.InlineKeyboardButton("АСЭ", callback_data='2'))
                markup.add(types.InlineKeyboardButton("Общежития", callback_data='3'))
                markup.add(types.InlineKeyboardButton("Военный учёт", callback_data='4'))
                markup.add(types.InlineKeyboardButton("Назад", callback_data='5'))
                botTimeWeb.send_message(function_call.message.chat.id, second_mess, reply_markup=markup)
                botTimeWeb.answer_callback_query(function_call.id)
            case "5":
                startBot(function_call.message)

botTimeWeb.infinity_polling()