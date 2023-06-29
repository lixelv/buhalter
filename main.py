from webhook import webhook_pooling
from aiogram.types import Message, CallbackQuery
from aiogram import executor
from url import *
from db import DB

# need in environ TELEGRAM and PORT

d = DB('data.sqlite3')

@dp.message_handler(commands=['start', 'help'])
async def start(message: Message):
    kb = None if d.user_exist(message.from_user.id) else currency
    await bot.send_message(
        message.from_user.id,
        'Привет ' + message.from_user.first_name + ' я <strong>Ваш бухгалтер</strong>\nЯ был разработан @simeonlimon, при возникновении проблем обращайтесь',
        parse_mode='HTML',
        reply_markup=kb)

@dp.message_handler(commands=['plus', 'minus'])
async def plus_minus_value(message: Message):
    if bool(i_n_t(message.get_args())):
        if message.get_command() == '/plus':
            d.add_data(message.from_user.id, message.get_args(), pm='plus')
            await bot.send_message(message.from_user.id, f'Добавлено зачисление в {message.get_args()} {d.currency(message.from_user.id)}')
        else:
            d.add_data(message.from_user.id, message.get_args(), pm='minus')
            await bot.send_message(message.from_user.id, f'Добавлено расход {message.get_args()} {d.currency(message.from_user.id)}')
    else:
        await bot.send_message(message.from_user.id, 'Вы ввели не число')

@dp.message_handler(commands=['h', 'his', 'history'])
async def history(message: Message):
    await bot.send_message(message.from_user.id, 'Выберете период за который показать историю', reply_markup=period)

@dp.message_handler(commands=['r', 'remove'])
async def remove_last(message: Message):
    d.del_last(message.from_user.id)
    await bot.send_message(message.from_user.id, 'Последняя запись была удалена')

@dp.callback_query_handler(lambda callback: callback.data in ['$', '€', '₽'])
async def add_currency(callback: CallbackQuery):
    d.new_user(callback.from_user.id, callback.from_user.first_name, callback.data)
    await callback.message.edit_text(f'Вы выбрали валюту: {callback.data}\nДобро пожаловать')

@dp.callback_query_handler(lambda callback: callback.data in ['day', 'week', 'month', 'year', 'whole_time'])
async def history_callback(callback: CallbackQuery):
    data = d.history(callback.from_user.id, period=callback.data)
    curr = d.currency(callback.from_user.id)
    msg = 'Вот ваша история:\n'
    for _ in data[0]:
        msg += f'{"➕" if _[0] == "plus" else "➖"} {_[1]} {curr}, {_[2]}\n'
    msg += f'\nБаланс: {data[1]}'
    await callback.message.edit_text(msg)

if __name__ == "__main__":
    webhook_pooling(dp, token, port=environ['PORT'])
