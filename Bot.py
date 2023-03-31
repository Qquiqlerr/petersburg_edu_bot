from telebot.async_telebot import AsyncTeleBot
import asyncio
from telebot import types, asyncio_filters
import json
from tables import *
import all_funcs
import pysondb as db
import os
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup


class WorkStates(StatesGroup):
    reg = State()
    work = State()
    per = State()
    reply_to = State()
    work_start = State()


with open('token.json','r') as t:
    token = json.load(t)
bot = AsyncTeleBot(token['token'],state_storage=StateMemoryStorage())


funcs = types.ReplyKeyboardMarkup()

database = db.getDb('user_info.json')

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
async def hello_and_reg(msg):
    await bot.send_message(msg.chat.id,"Привет! Давай начнем!")
    if len(database.getByQuery(query={"user_id": msg.chat.id})) == 0:
        await bot.set_state(msg.from_user.id, WorkStates.reg, msg.chat.id)
        await bot.send_message(msg.chat.id, "Введите логин и пароль в формате\n"
                                            "Login:pass")
        print(await bot.get_state(msg.from_user.id, msg.chat.id))
    else:
        await bot.set_state(msg.from_user.id, WorkStates.reply_to, msg.chat.id)
        await reply_to(msg)
@bot.message_handler(state= WorkStates.reg)
async def reg(msg):
    try:
        data = all_funcs.create_data(msg.text)
        all_funcs.auth_and_create_cookies(data, msg.chat.id)
        await reply_to(msg)
    except Exception:
        await bot.send_message(msg.chat.id,"Что-то пошло не так( \n"
                                     "Попробуйте еще раз, или обратитесь к админу")
        await hello_and_reg(msg)




@bot.message_handler(state=WorkStates.work)
async def work(msg):
    print('dgfiomvbcoi')
    if msg.text == 'Оценки за период':
        await bot.send_message(msg.chat.id, 'Отлично! Выбери период', reply_markup=marks_per_markup)
        await bot.set_state(msg.from_user.id, WorkStates.per, msg.chat.id)
    elif msg.text == 'Текущие оценки':
        info = all_funcs.get_current_marks(msg.chat.id)
        for i in info:
            await bot.send_message(msg.chat.id, i)
    elif msg.text == 'Назад':
        await reply_to(msg)

@bot.message_handler(state=WorkStates.per)
async def per(msg):
    if msg.text == 'Оценки за первое полугодие':
        await bot.send_message(msg.chat.id, all_funcs.get_marks(msg.chat.id, 'first_half'))
    elif msg.text == 'Оценки за второе полугодие':
        await bot.send_message(msg.chat.id, all_funcs.get_marks(msg.chat.id, 'second_half'))
    elif msg.text == 'Оценки за год':
        await bot.send_message(msg.chat.id, all_funcs.get_marks(msg.chat.id, 'year'))
    elif msg.text == 'Назад':
        await work_start(msg)

@bot.message_handler(state= WorkStates.reply_to)
async def reply_to(msg):
    await bot.send_message(msg.chat.id,"Выберите одну из доступных опций",reply_markup=funcs)
    await bot.set_state(msg.from_user.id, WorkStates.work_start, msg.chat.id)

@bot.message_handler(state= WorkStates.work_start)
async def work_start(msg):
    await bot.send_message(msg.chat.id,'Отлично! Выбери, что тебе нужно',reply_markup=marks_markup)
    await bot.set_state(msg.from_user.id, WorkStates.work, msg.chat.id)



bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())

asyncio.run(bot.infinity_polling())
