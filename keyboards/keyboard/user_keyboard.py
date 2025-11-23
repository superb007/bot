from data.config import cr_test, dl_test, shw_ans, check_ans, results
from aiogram import types

btn = [
    [
        types.KeyboardButton(text=check_ans)
    ],
    [
        types.KeyboardButton(text=results)
    ]
]

user_markup = types.ReplyKeyboardMarkup(keyboard=btn, resize_keyboard=True)

contact_button = types.KeyboardButton(text="📱 Share Contact", request_contact=True)
request_contact_markup = types.ReplyKeyboardMarkup(keyboard=[[contact_button]], resize_keyboard=True)