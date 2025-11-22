from aiogram import Router, F, types
from data import config
from data.config import refresh_txt

from filters import AdminFilter
from keyboards.inline import refresh
from loader import db

stater = Router()
stater.message.filter(AdminFilter())
stater.callback_query.filter(AdminFilter())

@stater.message(F.text==config.stats)
async def show_stats(message: types.Message):
    users = db.fetchone("SELECT COUNT(*) FROM user")[0]
    submissions = db.fetchone("SELECT COUNT(*) FROM submissions")[0]
    exams = db.fetchone("SELECT COUNT(*) FROM exams")[0]
    await message.answer(f"#️⃣The numbers are provided below:\n<b>👤Users registered</b> - {users}\n<b>📥Submissions</b> - {submissions}\n<b>📝Exams</b> - {exams}", reply_markup=refresh)