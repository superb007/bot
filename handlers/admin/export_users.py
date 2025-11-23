import io
import csv
from aiogram import Router, F, types
from filters import AdminFilter
from loader import db
from data import config

export_router = Router()
export_router.message.filter(AdminFilter())

@export_router.message(F.text == config.users_csv)
async def export_users_csv(message: types.Message):
    await message.answer("🔄 Generating the CSV file...")
    users = db.fetchall('SELECT userid, fullname, surname, username, contact, regdate FROM user')
    
    if not users:
        await message.answer("No users found in the database.")
        return

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['UserID', 'Full Name', 'Surname', 'Username', 'Contact', 'Registration Date'])

    # Write user data
    for user in users:
        writer.writerow(user)

    output.seek(0)
    
    csv_file = types.BufferedInputFile(output.getvalue().encode('utf-8'), filename='users.csv')
    
    await message.answer_document(csv_file, caption="👥 Here is the list of all users.")
