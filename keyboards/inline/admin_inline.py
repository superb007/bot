from aiogram import types
from data.config import cancel, confirm, one_by_one, all_at_one, all_at_one_checked, one_by_one_checked, nm_ans, \
    shw_ans, archive, end_exam, refresh_txt

btn = [
    [
        types.InlineKeyboardButton(text=cancel, callback_data="admin_cancel"),
        types.InlineKeyboardButton(text=confirm, callback_data="admin_confirm"),
    ]
]
confirm_admin = types.InlineKeyboardMarkup(inline_keyboard=btn)

btn1 = [
    [
        types.InlineKeyboardButton(text=all_at_one_checked, callback_data="all_at_one_checked"),
        types.InlineKeyboardButton(text=one_by_one, callback_data="one_by_one"),
    ]
]
all_checked = types.InlineKeyboardMarkup(inline_keyboard=btn1)

btn2 = [
    [
        types.InlineKeyboardButton(text=all_at_one, callback_data="all_at_one"),
        types.InlineKeyboardButton(text=one_by_one_checked, callback_data="one_by_one_checked"),
    ]
]
one_checked = types.InlineKeyboardMarkup(inline_keyboard=btn2)

btn3 = [
    [
        types.InlineKeyboardButton(text=nm_ans, callback_data="show_results"),
        types.InlineKeyboardButton(text=shw_ans, callback_data="show_ans"),
    ],
    [
        types.InlineKeyboardButton(text=end_exam, callback_data="end_exam"),
    ]
]
exam_con = types.InlineKeyboardMarkup(inline_keyboard=btn3)

btn4 = [
    [
        types.InlineKeyboardButton(text=refresh_txt, callback_data="refresh"),
    ]
]
refresh = types.InlineKeyboardMarkup(inline_keyboard=btn4)