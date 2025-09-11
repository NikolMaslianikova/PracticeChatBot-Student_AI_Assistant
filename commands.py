from aiogram import types
from aiogram.filters import Command
from keyboards import subject_kb, style_kb, lectures_kb
from user_data import user_subject, user_style, user_lecture
from prompts import SUBJECT_READABLE

def func_commands(dp):
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(
            "Привіт! 👩‍💻 Я твій навчальний помічник.\n"
            "Обери предмет, з яким ми будемо працювати:",
            reply_markup=subject_kb()
        )

    @dp.message(Command("stop"))
    async def cmd_stop(message: types.Message):
        uid = message.from_user.id
        user_subject.pop(uid, None)
        user_style.pop(uid, None)
        user_lecture.pop(uid, None)
        await message.answer("Розмову завершено.\nЩоб почати нову — напиши /start")

    @dp.message(Command("status"))
    async def cmd_status(message: types.Message):
        subj = user_subject.get(message.from_user.id)
        style = user_style.get(message.from_user.id)
        lec = user_lecture.get(message.from_user.id)
        await message.answer(
            "Статус:\n"
            f"Предмет: {SUBJECT_READABLE.get(subj, '—')}\n"
            f"Стиль: {style or '—'}\n"
            f"Лекція: {lec or '—'}\n\n"
            "Щоб змінити: /start"
        )

    @dp.message(Command("subject"))
    async def cmd_subject(message: types.Message):
        await message.answer("Обери предмет:", reply_markup=subject_kb())

    @dp.message(Command("style"))
    async def cmd_style(message: types.Message):
        if message.from_user.id not in user_subject:
            await message.answer("Спочатку обери предмет: /start"); return
        await message.answer("Обери стиль відповіді:", reply_markup=style_kb())

    @dp.message(Command("lectures"))
    async def cmd_lectures(message: types.Message):
        uid = message.from_user.id
        if uid not in user_subject:
            await message.answer("Спочатку обери предмет: /start"); return
        if uid not in user_style:
            await message.answer("Спочатку обери стиль відповіді: /style"); return
        await message.answer("Обери лекцію:", reply_markup=lectures_kb(user_subject[uid]))
