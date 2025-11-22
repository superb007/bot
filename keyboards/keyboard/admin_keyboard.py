from data.config import cr_test, main_menu, back, skip, running_exams, archive, stats, help_txt
from aiogram import types

btn = [
    [
        types.KeyboardButton(text=cr_test)
    ],
    [
        types.KeyboardButton(text=running_exams),
        types.KeyboardButton(text=archive)

    ],
    [
        types.KeyboardButton(text=help_txt),
        types.KeyboardButton(text=stats)
    ]
]

admin_markup = types.ReplyKeyboardMarkup(keyboard=btn, resize_keyboard=True)

btn1 = [
    [
        types.KeyboardButton(text=main_menu)
    ]
]
main_markup = types.ReplyKeyboardMarkup(keyboard=btn1, resize_keyboard=True)

btn2 = [
    [
        types.KeyboardButton(text=back),
        types.KeyboardButton(text=skip)
    ],
    [
        types.KeyboardButton(text=main_menu)
    ]
]
in_bet = types.ReplyKeyboardMarkup(keyboard=btn2, resize_keyboard=True)

btn3 = [
    [
        types.KeyboardButton(text=back)
    ],
    [
        types.KeyboardButton(text=main_menu)
    ]
]
num_quests = types.ReplyKeyboardMarkup(keyboard=btn3, resize_keyboard=True)