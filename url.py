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