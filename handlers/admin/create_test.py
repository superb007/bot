from pyexpat.errors import messages

from data import config
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from data.config import MAX_EXAMS_AT_A_TIME
from utils.funs import g_code
from keyboards.inline import confirm_admin, all_checked, one_checked
from keyboards.keyboard import main_markup, admin_markup, in_bet, num_quests
from states import create_states
from loader import db
from filters import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())

@admin_router.message(Command("create"))
@admin_router.message(F.text == config.cr_test)
async def create_test(message: types.Message, state: FSMContext):
    alr = db.fetchone("SELECT COUNT(*) FROM exams")[0]
    if alr==MAX_EXAMS_AT_A_TIME:
        await message.answer("You exceeded the number of tests can be run at a time.")
        return
    # await message.reply("👇 Here, you can create a new test.\n⚠️ Make sure to check if a duplicate isn't already active.")
    response = "Please, send the title of the test:"
    await state.set_state(create_states.title)
    await message.answer(response, reply_markup=main_markup)
    #
    # alr = db.fetchone("SELECT correct FROM current")
    # if alr is None:
    #     await message.answer("Send the correct answers in this format:\n\t<code>4 abcabc...</code>\n\nP.S. - 4 means four options", reply_markup=main_markup)
    #     await state.set_state(create_states.correct_answer)
    # else:
    #     await message.answer("Delete the current one first")

@admin_router.message(create_states.title)
async def take_title(message: types.Message, state: FSMContext):
    t = message.text
    await state.update_data(title=t)
    await state.set_state(create_states.about)
    await message.answer(f"<b>Title:</b> {t}\n\nPlease, send the description:", reply_markup=in_bet)

@admin_router.message(create_states.about, F.text == config.back)
async def back_to_title(message: types.Message, state: FSMContext):
    await state.set_state(create_states.title)
    await create_test(message, state)

@admin_router.message(create_states.about, F.text == config.skip)
async def skip_to_questnum(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(about="__skip")
    await state.set_state(create_states.num_quest)
    await message.answer(f"<b>Title:</b> {data["title"]}\n<s>Description skipped</s>\n\nPlease, send the number of questions:", reply_markup=num_quests)

@admin_router.message(create_states.about)
async def about(message: types.Message, state: FSMContext):
    data = await state.get_data()
    a = message.text
    await state.update_data(about=a)
    await state.set_state(create_states.num_quest)
    await message.answer(f"<b>Title:</b> {data["title"]}\n<b>Description:</b> {a}\n\nPlease, send the number of questions:", reply_markup=num_quests)

@admin_router.message(create_states.num_quest, F.text == config.back)
async def back_to_about(message: types.Message, state: FSMContext):
    data = await state.get_data()
    response = f"<b>Title:</b> {data['title']}"
    response += (f"\n\nPlease, send the description:" if data["about"]!="__skip" else "\n\nPlease, send the description:")
    await state.set_state(create_states.about)
    await message.answer(response, reply_markup=in_bet)

@admin_router.message(create_states.num_quest)
async def process_num(message: types.Message, state: FSMContext):
    num = int()
    try:
        num = int(message.text)
    except Exception:
        await message.answer("Please, enter a valid number")
        return
    if 0 < num <= 50:
        data = await state.get_data()
        response = f"<b>Title:</b> {data['title']}"
        response += f"\n<b>Description:</b> {data["about"]}" if data["about"]!="__skip" else ""
        response += f"\n<b>Number of questions:</b> {num}\n\n"
        await state.update_data(num_quest=num)
        await state.set_state(create_states.correct_answer)
        await state.update_data(mode=1)
        await state.update_data(current=1)
        await state.update_data(correct="")
        response += "You can send the correct answers in either of this way. Change as you please and send them:"
        await message.answer(response, reply_markup=all_checked)
    else:
        await message.answer("Please, enter a number in range of 1 to 50 to provide good user experience")

@admin_router.message(create_states.correct_answer, F.text == config.back)
async def back_to_num(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data["current"]>1:
        cnt = data["current"]
        await state.update_data(current=cnt-1)
        correct = data["correct"]
        if cnt == 2:
            await state.update_data(correct="")
        else:
            correct = correct[:-2-correct[::-1].find("__")]
            await state.update_data(correct=correct)
        await message.answer(f"Send the answer for question number <b>{cnt-1}</b>")
    else:
        response = f"<b>Title:</b> {data['title']}"
        response += f"\n<b>Description:</b> {data["about"]}" if data["about"] != "__skip" else ""
        response += "\n\nPlease, enter the number of questions:"
        await state.set_state(create_states.num_quest)
        await message.answer(response, reply_markup=num_quests)

@admin_router.callback_query(create_states.correct_answer)
async def process_checking(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    n = data["current"]
    if callback.data == "all_at_one_checked":
        await callback.answer("Already chosen")
    elif callback.data == "one_by_one":
        await callback.answer("One by one")
        await state.update_data(mode=2)
        await callback.message.answer(f"Send the answer for question number <b>{n}</b>")
        await callback.message.edit_reply_markup(reply_markup=one_checked)
    elif callback.data == "one_by_one_checked":
        await callback.answer("Already chosen")
    elif callback.data == "all_at_one":
        await callback.answer("All at one")
        await state.update_data(mode=1)
        await callback.message.answer(f"<b>{n-1}</b> answers were given with one-by-one method. Please, send the others, starting with the answer for question number {n}, at once.")
        await callback.message.edit_reply_markup(reply_markup=all_checked)

@admin_router.message(create_states.correct_answer)
async def taking_answers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cnt = data["current"]
    n_questions = int(data["num_quest"])
    if data["mode"] == 1:
        raw = message.text.split("\n")
        correct = data["correct"]
        for line in range(len(raw)):
            if raw[line] != "":
                correct += ("__" if cnt>1 else "") + raw[line]
                cnt+=1
        if cnt == n_questions+1:
            await state.update_data(correct=correct)
            await state.set_state(create_states.confirm)
            await message.answer(f"Can you confirm your actions?", reply_markup=confirm_admin)
        else:
            await message.answer("The number of questions doesn't match the entered value. Please, enter correct number of answers or change the number of questions.", reply_markup=num_quests)
    else:
        correct = data["correct"]
        correct += ("__" if cnt >1 else "")+message.text
        await state.update_data(correct=correct)
        if cnt == n_questions:
            await state.set_state(create_states.confirm)
            await message.answer("You have done entering all the answers. Can you confirm your actions?", reply_markup=confirm_admin)
        else:
            cnt += 1
            await state.update_data(current=cnt)
            await message.answer(f"Send the answer for question number <b>{cnt}</b>")


# @admin_router.message(create_states.correct_answer)
# async def rec_correct_answer(message: types.Message, state: FSMContext):
#     raw = message.text.lower()
#     try:
#         option = int(raw.split()[0])
#     except Exception as e:
#         print(e)
#         await message.answer("Please, follow the format.")
#         await state.clear()
#         return
#     raw = raw.split()[1]
#     num = len(raw)
#     legit = True
#     for i in raw:
#         if i not in "abcdefghijklmnopqrstuvwxyz"[:option]:
#             legit = False
#             break
#     if legit:
#         response = f"Can you confirm the test has {num} answers and they are as follows:\n"
#         for i in range(num):
#             response += f"{i+1}.{raw[i].upper()}"
#             if i != num-1:
#                 response += ", "
#         await message.reply(response, reply_markup=confirm_admin)
#         await state.update_data(corr=raw)
#         await state.update_data(option=option)
#         await state.set_state(create_states.confirm)
#     else:
#         await message.answer("The answer include an option that's not legit")

@admin_router.callback_query(create_states.confirm)
async def create_confirm(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if callback.data == "admin_confirm":
        corr = data["correct"]
        n_questions = int(data["num_quest"])
        title = data["title"]
        ab = data["about"]
        code = g_code()
        from_db = db.fetchone("SELECT * FROM exams WHERE code = ?", (code,))
        while from_db is not None:
            code = g_code()
            from_db = db.fetchone("SELECT * FROM exams WHERE code = ?", (code,))
        db.query("INSERT INTO exams(code, title, about, num_questions, correct, running) VALUES (?,?,?,?,?,?)", (code, title, ab, n_questions, corr, 1))
        await callback.message.answer("Test created. Check the test in the ⚡️ Running tests menu")
        await callback.answer("Confirmed")
    elif callback.data == "admin_cancel":
        await callback.message.answer("Test creation cancelled")
        await callback.answer("Cancelled")
    await callback.bot.send_message(callback.message.chat.id, "You've been brought to 🏠 Main menu.", reply_markup=admin_markup)
    await callback.message.delete()
    await state.clear()

@admin_router.message(create_states.confirm, F.text == config.back)
async def back_to_receiving(message: types.Message, state: FSMContext):
    data = await state.get_data()
    response = f"<b>Title:</b> {data['title']}"
    response += f"\n<b>Description:</b> {data["about"]}" if data["about"] != "__skip" else ""
    response += f"\n<b>Number of questions:</b> {data["num_quest"]}\n\n"
    await state.set_state(create_states.correct_answer)
    await state.update_data(mode=1)
    await state.update_data(current=1)
    await state.update_data(correct="")
    response += "You can send the correct answers in either of this way. Change as you please and send them:"
    await message.answer(response, reply_markup=all_checked)




# @admin_router.message(Command("answers"))
# @admin_router.message(F.text == config.shw_ans)
# async def shw_answer(message: types.Message, state: FSMContext):
#     ans = db.fetchone("SELECT correct FROM current")
#     if ans is not None:
#         ans=ans[0]
#         response = f"The test has {len(ans)} questions. The correct answers are as follows:\n"
#         for i in range(len(ans)):
#             response += f"{i+1}. {ans[i].upper()}"
#             if i != len(ans) - 1:
#                 response += ", "
#         await message.answer(response)
#     else:
#         await message.answer("There is no test active right now. Create one first")

# @admin_router.message(Command("del"))
# @admin_router.message(F.text == config.dl_test)
# async def delete_test(message: types.Message, state: FSMContext):
#     alr = db.fetchone("SELECT correct FROM current")
#     if alr is not None:
#         await message.answer("Can you confirm you want to delete the test", reply_markup=confirm_admin)
#         await state.set_state(del_states.confirm)
#         db.create_tables()
#     else:
#         await message.answer("There is no test active right now. Create one first")

# @admin_router.callback_query(del_states.confirm)
# async def delete_confirm(callback: types.CallbackQuery, state: FSMContext):
#     if callback.data == "admin_confirm":
#         db.query("DELETE FROM current")
#         db.query("DELETE FROM user")
#         await callback.message.answer("Test deleted")
#         await callback.answer("Confirmed")
#         await state.clear()
#     elif callback.data == "admin_cancel":
#         await callback.message.answer("Test deletion cancelled. You can resend the right answers.")
#         await callback.answer("Cancelled")
#     await callback.message.delete()

# @admin_router.message(Command("results"))
# @admin_router.message(F.text == config.nm_ans)
# async def nm_answer(message: types.Message):
#     alr = db.fetchone("SELECT correct FROM current")
#     if alr is not None:
#         raw = db.fetchall("SELECT idx, fullname, answered FROM user ORDER BY answered DESC")
#         if len(raw) > 0:
#             response = "The results of the test is as follows:\n"
#             for i in range(len(raw)):
#                 response += f"{i + 1}. {raw[i][1]} - {raw[i][2]}\n"
#             await message.answer(response)
#         else:
#             await message.answer("No one has answered yet")
#     else:
#         await message.answer("There is no test active right now. Create one first")