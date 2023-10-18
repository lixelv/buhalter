# from webhook import webhook_pooling
from aiogram.types import Message, CallbackQuery
from aiogram import executor
from time import sleep
from url import *
from db import DB

# need in environ TELEGRAM and PORT

d = DB('data.sqlite3')

@dp.message_handler(commands=['start', 'help'])
async def start(message: Message):
    if d.user_exist(message.from_user.id):
        kb, i = None, ''
    else:
        kb, i = currency, '\nВыберете вашу валюту:'
    kb = None if d.user_exist(message.from_user.id) else currency
    await bot.send_message(
        message.from_user.id,
        f'Привет {message.from_user.first_name} я <strong>Ваш бухгалтер</strong>. Я был разработан @simeonlimon, при возникновении проблем обращайтесь.{i}',
        parse_mode='HTML',
        reply_markup=kb)

@dp.message_handler(commands=['plus', 'p', 'minus', 'm'])
async def plus_minus_value(message: Message):
    args = convert_to_number(message.get_args())
    if bool(args):
        if message.get_command() in ['/plus', '/p']:
            d.add_data(message.from_user.id, args, pm='plus')
            await bot.send_message(message.from_user.id, f'Добавлено зачисление в {args} {d.currency(message.from_user.id)}')
        else:
            d.add_data(message.from_user.id, args, pm='minus')
            await bot.send_message(message.from_user.id, f'Добавлено расход {args} {d.currency(message.from_user.id)}')
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
    msg += f'\nБаланс: {data[1]} {d.currency(callback.from_user.id)}'
    await callback.message.edit_text(msg)

if __name__ == "__main__":
    # webhook_pooling(dp, token, port=port)
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
            
        except KeyboardInterrupt:
            print("Выход...")
            break
        
        except Exception as e:
            print(e)
            sleep(240)
            