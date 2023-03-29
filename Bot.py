import telebot
from telebot import types
import json
from tables import *
import all_funcs
import os
with open('token.json','r') as t:
    token = json.load(t)
bot = telebot.TeleBot(token['token'])
a = ''

type_codes = [
    ['first_half_year', 30, ]
]

funcs = types.ReplyKeyboardMarkup()

marks = types.KeyboardButton('Оценки')
funcs.add(marks)

marks = [types.KeyboardButton('Оценки за период'),
         types.KeyboardButton('Текущие оценки'),
         types.KeyboardButton('Назад')]

marks_per = [types.KeyboardButton('Оценки за первое полугодие'),
             types.KeyboardButton('Оценки за второе полугодие'),
             types.KeyboardButton('Оценки за год'),
             types.KeyboardButton('Назад')
]

marks_markup = types.ReplyKeyboardMarkup()
for i in marks:
    marks_markup.add(i)

marks_per_markup = types.ReplyKeyboardMarkup()
for i in marks_per:
    marks_per_markup.add(i)





@bot.message_handler(commands=['start'])
def hello_and_reg(msg):
    bot.send_message(msg.chat.id,"Привет! Давай начнем!")
    if not os.path.isdir(f"User_info/{msg.chat.id}"):
        send = bot.send_message(msg.chat.id, "Введите логин и пароль в формате\n"
                                      "Login:pass")
        bot.register_next_step_handler(send, reg)
    else:
        reply_to(msg)
def reg(msg):
    try:
        data = all_funcs.create_data(msg.text)
        all_funcs.auth_and_create_cookies(data, msg.chat.id)
        reply_to(msg)
    except Exception:
        bot.send_message(msg.chat.id,"Что-то пошло не так( \n"
                                     "Попробуйте еще раз, или обратитесь к админу")
        hello_and_reg(msg)
    return 0
def reply_to(msg):
    bot.send_message(msg.chat.id,"Отлично! Выберите одну из доступных опций",reply_markup=funcs)

@bot.message_handler(content_types=['text'])
def work_start(msg):
    bot.send_message(msg.chat.id,'Отлично! Выбери, что тебе нужно',reply_markup=marks_markup)
    bot.register_next_step_handler(msg,work)
def work(msg):
    if msg.text == 'Оценки за период':
        bot.send_message(msg.chat.id, 'Отлично! Выбери период', reply_markup=marks_per_markup)
        bot.register_next_step_handler(msg, per)
    elif msg.text == 'Текущие оценки':
        info = all_funcs.get_current_marks(msg.chat.id)
        for i in info:
            bot.send_message(msg.chat.id, i)
        bot.register_next_step_handler(msg, work)
    elif msg.text == 'Назад':
        reply_to(msg)
def per(msg):
    if msg.text == 'Оценки за первое полугодие':
        bot.send_message(msg.chat.id, all_funcs.get_marks(msg.chat.id, 'first_half'))
        bot.register_next_step_handler(msg, per)
    elif msg.text == 'Оценки за второе полугодие':
        bot.send_message(msg.chat.id, all_funcs.get_marks(msg.chat.id, 'second_half'))
        bot.register_next_step_handler(msg, per)
    elif msg.text == 'Оценки за год':
        bot.send_message(msg.chat.id, all_funcs.get_marks(msg.chat.id, 'year'))
        bot.register_next_step_handler(msg, per)
    elif msg.text == 'Назад':
        work_start(msg)




bot.infinity_polling()
