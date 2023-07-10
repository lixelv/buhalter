db.py:
```python
import sqlite3
from url import unt

class DB:
    def __init__(self, db_name):
        self.connect = sqlite3.connect(db_name)
        self.cursor = self.connect.cursor()
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    name TEXT,
    currency TEXT NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
    );""")
        self.cursor.execute("""
CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pm TEXT NOT NULL,
    value INTEGER NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP
);""")
        self.connect.commit()

    def user_exist(self, user_id) -> bool:
        result = self.cursor.execute('SELECT id FROM user WHERE id = ?', (user_id,))
        return bool(len(result.fetchall()))

    def new_user(self, user_id, username, currency) -> None:
        if not self.user_exist(user_id):
            self.cursor.execute('INSERT INTO user(id, name, currency) VALUES (?, ?, ?)', (user_id, username, currency))
            self.connect.commit()
        else:
            pass

    def currency(self, user_id) -> str:
        self.cursor.execute('SELECT currency FROM user WHERE id = ?', (user_id,))
        return self.cursor.fetchone()[0]

    def add_data(self, user_id, value, pm: str) -> None:
        self.cursor.execute('INSERT INTO data(user_id, value, pm) VALUES (?,?,?)', (user_id, value, pm))
        self.connect.commit()

    def history(self, user_id, period: str = 'whole_time') -> list:
        result: list = []
        balance: float = 0
        t = 'start of year'
        if period != 'whole_time':
            if period == 'day':
                t: str = 'start of day'
            elif period == 'week':
                t: str = '-6 days'
            elif period == 'month':
                t: str = 'start of month'
            elif period == 'year':
                t: str = 'start of year'
            self.cursor.execute(f"SELECT pm, value, date FROM data WHERE user_id = ? and date BETWEEN datetime('now', '{t}') AND datetime('now', 'localtime') ORDER BY date", (user_id,))
            result = self.cursor.fetchall()
            self.cursor.execute(f"SELECT value FROM data WHERE user_id = ? and pm= 'plus' and date BETWEEN datetime('now', '{t}') AND datetime('now', 'localtime')", (user_id,))
            sum_1 = sum(unt(self.cursor.fetchall()))
            self.cursor.execute(f"SELECT value FROM data WHERE user_id = ? and pm = 'minus' and date BETWEEN datetime('now', '{t}') AND datetime('now', 'localtime')", (user_id,))
            sum_2: int = sum(unt(self.cursor.fetchall()))
        else:
            self.cursor.execute(f"SELECT pm, value, date FROM data WHERE user_id = ? ORDER BY date", (user_id,))
            result = self.cursor.fetchall()
            self.cursor.execute("SELECT value FROM data WHERE user_id = ? and pm = 'plus'", (user_id,))
            sum_1: int = sum(unt(self.cursor.fetchall()))
            self.cursor.execute("SELECT value FROM data WHERE user_id = ? and pm = 'minus'", (user_id,))
            sum_2: int = sum(unt(self.cursor.fetchall()))
        res = sum_1 - sum_2
        return [result, res]

    def del_last(self, user_id) -> None:
        self.cursor.execute('DELETE FROM data WHERE date = (SELECT MAX(date) FROM data WHERE user_id = ?) and user_id = ?', (user_id, user_id))
        self.connect.commit()
```
main.py:
```python
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

```
test.py:
```python
from url import *

def main():
    print(sum(unt([(10,), (20,)])))


if __name__ == '__main__':
    main()

```
url.py:
```python
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from os import environ

token = environ['TELEGRAM']
bot = Bot(token)
dp = Dispatcher(bot)

def unt(lis):
    result: list = []
    for _ in lis:
        result.append(_[0])
    return result

def i_n_t(data):
    try:
        return int(data)
    except:
        return False

def inline_keyboard(list_of_values: list = None, list_of_callback_data: list = None, valcal: bool = False) -> InlineKeyboardMarkup:
    if valcal:
        list_of_callback_data = list_of_values
    kb = InlineKeyboardMarkup(row_width=len(list_of_values[0]))
    buttons: list = []
    for value, callback_data in zip(list_of_values, list_of_callback_data):
        for v, c in zip(value, callback_data):
            buttons.append(InlineKeyboardButton(v, callback_data=c))
    kb.add(*buttons)
    return kb

currency = inline_keyboard([['$', '€', '₽']], valcal=True)
period = inline_keyboard([['день', 'неделя', 'месяц'],
                          ['год', 'все время']],
                         [['day', 'week', 'month'],
                          ['year', 'whole_time']])
```
