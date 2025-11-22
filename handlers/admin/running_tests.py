from aiogram import Router, F, types
from pyexpat.errors import messages

from keyboards.inline import exam_con, confirm_admin, refresh
from states.r_exams_states import del_states, end_states, edit_states, edit_about_states
from aiogram.fsm.context import FSMContext

from filters import AdminFilter
from aiogram.filters import Command
from loader import db
from data import config
from .stats import show_stats

r_test = Router()
r_test.message.filter(AdminFilter())
r_test.callback_query.filter(AdminFilter())

@r_test.message(Command("running"))
@r_test.message(F.text == config.running_exams)
async def running(message: types.Message):
    r_exams = db.fetchall("SELECT * FROM exams WHERE running = 1")
    if len(r_exams) == 0:
        await message.answer("There is no exams running")
        return
    for exam in r_exams:
        response = f"<b>Title:</b> {exam[2]}"
        response += f"\n<b>Description:</b> {exam[3]}" if exam[3]!="__skip" else ""
        response += f"\n<b>Number of questions:</b> {exam[4]}"
        btn = [
            [
                types.InlineKeyboardButton(text=config.edit_title, callback_data=f"edit_title_{exam[0]}"),
                types.InlineKeyboardButton(text=config.edit_about, callback_data=f"edit_about_{exam[0]}")
            ],
            [
                types.InlineKeyboardButton(text=config.nm_ans, callback_data=f"show_results_{exam[0]}"),
                types.InlineKeyboardButton(text=config.shw_ans, callback_data=f"show_ans_{exam[0]}"),
            ],
            [
                types.InlineKeyboardButton(text=config.share, callback_data=f"share_{exam[0]}")
            ],
            [
                types.InlineKeyboardButton(text=config.end_exam, callback_data=f"end_{exam[0]}"),
            ]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=btn)
        await message.answer(response, reply_markup=markup)
    await message.answer("👆 These are the running tests")

@r_test.callback_query()
async def process_utils(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith("show_results_"):
        exid = callback.data.split("_")[2]
        submissions = db.fetchall("SELECT * FROM submissions WHERE exid = ? ORDER BY corr DESC, date", (exid,))
        # print(submissions)
        if len(submissions) == 0:
            await callback.answer("No submission yet")
            await callback.message.reply("No submission found for the test")
            return
        response = "These are the top results for the test:\nPlace - Name - Correct answers"
        for sub in range(len(submissions)):
            user_info = db.fetchone("SELECT * FROM user WHERE userid = ?", (submissions[sub][2],))
            if user_info[3] != "None":
                response += f"\n{"🥇" if sub==0 else "🥈" if sub==1 else "🥉" if sub==2 else sub+1} - <a href='https://t.me/{user_info[3]}'><b>{user_info[2]}</b></a> - {submissions[sub][4]}"
            else:
                response += f"\n{"🥇" if sub==0 else "🥈" if sub==1 else "🥉" if sub==2 else sub+1} - <b>{user_info[2]}</b>"
        await callback.message.reply(response, disable_web_page_preview=True)
    elif callback.data.startswith("share_"):
        exid = callback.data.split("_")[1]
        code = db.fetchone("SELECT code FROM exams WHERE idx = ?", (exid,))[0]
        response = f"You can share this following link, so that users will quickly start answering to the test:\n\n<code>https://t.me/{config.bot_info.username}?start=code-{code}</code>\n\nor share this code which users will enter to start answering\n\n<code>{code}</code>"
        text_to_share = f"Participate in this exam:\nhttps://t.me/{config.bot_info.username}?start=code-{code}"
        btn = [
            [types.InlineKeyboardButton(text=config.share, switch_inline_query=text_to_share)]
        ]
        markup = types.InlineKeyboardMarkup(inline_keyboard=btn)
        await callback.message.reply(response, reply_markup=markup)
    elif callback.data.startswith("show_ans_"):
        exid = callback.data.split("_")[2]
        correct = list(db.fetchone("SELECT correct FROM exams WHERE idx = ?", (exid,))[0].split("__"))
        response = "✅ The correct solutions for the test are as follows:"
        for i in range(len(correct)):
            response += f"\n<b># {i+1}</b>: {correct[i]}"
        await callback.message.reply(response)
    elif callback.data.startswith("edit_title_"):
        exid = callback.data.split("_")[2]
        await state.update_data(exid=exid)
        await state.set_state(edit_states.name)
        await callback.message.reply("Send the new title:")
    elif callback.data.startswith("edit_about_"):
        exid = callback.data.split("_")[2]
        await state.update_data(exid=exid)
        await state.set_state(edit_about_states.about)
        await callback.message.reply("Send the new description:")
    elif callback.data.startswith("end_"):
        exid = callback.data.split("_")[1]
        await state.update_data(exid=exid)
        await state.set_state(end_states.confirm)
        await callback.message.reply("Can you confirm you want to end the test and archive it?", reply_markup=confirm_admin)
    elif callback.data == "admin_confirm":
        data = await state.get_data()
        db.query("UPDATE exams SET running = 0 WHERE idx = ?", (data["exid"],))
        await callback.answer("Confirmed")
        await callback.message.answer("The test has ended and been added to archive.")
        await state.clear()
        await callback.message.delete()
    elif callback.data == "admin_cancel":
        await callback.answer("Cancelled")
        await callback.message.answer("Ending the test has been cancelled.")
        await state.clear()
        await callback.message.delete()
    elif callback.data == "refresh":
        users = db.fetchone("SELECT COUNT(*) FROM user")[0]
        submissions = db.fetchone("SELECT COUNT(*) FROM submissions")[0]
        exams = db.fetchone("SELECT COUNT(*) FROM exams")[0]
        try:
            await callback.message.edit_text(f"#️⃣The numbers are provided below:\n<b>👤Users registered</b> - {users}\n<b>📥Submissions</b> - {submissions}\n<b>📝Exams</b> - {exams}", reply_markup=refresh)
            await callback.answer("Refreshed")
        except Exception:
            await callback.answer("Nothing new")

@r_test.message(edit_states.name)
async def new_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.query("UPDATE exams SET title = ? WHERE idx = ?", (message.text,data["exid"]))
    await message.answer("Title updated")
    await state.clear()
    await running(message)

@r_test.message(edit_about_states.about)
async def new_about(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.query("UPDATE exams SET about = ? WHERE idx = ?", (message.text,data["exid"]))
    await message.answer("Description updated")
    await state.clear()
    await running(message)