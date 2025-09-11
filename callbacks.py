from aiogram import types
from keyboards import style_kb, lectures_kb
from user_data import user_subject, user_style, user_lecture
from prompts import SUBJECT_READABLE, PRESET_PROMPTS, lectures

def func_callbacks(dp):
    @dp.callback_query()
    async def handle_callback(callback: types.CallbackQuery):
        data = callback.data or ""
        uid = callback.from_user.id

        if data.startswith("subj:"):
            subj = data.split(":")[1]
            if subj not in lectures:
                await callback.answer("Невідомий предмет", show_alert=True)
                return
            user_subject[uid] = subj
            user_style.pop(uid, None)
            user_lecture.pop(uid, None)
            await callback.message.answer(
                f"Предмет: {SUBJECT_READABLE[subj]}\nОбери стиль відповіді:",
                reply_markup=style_kb()
            )
            await callback.answer()
            return

        if data.startswith("style:"):
            style_key = data.split(":")[1]
            if style_key not in PRESET_PROMPTS:
                await callback.answer("Невідомий стиль", show_alert=True)
                return
            user_style[uid] = style_key
            await callback.message.answer(
                "Стиль обрано.\nОбери лекцію:",
                reply_markup=lectures_kb(user_subject[uid])
            )
            await callback.answer()
            return

        if data.startswith("lec:"):
            _, subj, idx_str = data.split(":")
            idx = int(idx_str) - 1
            if subj not in lectures or idx < 0 or idx >= len(lectures[subj]):
                await callback.answer("Некоректна лекція", show_alert=True)
                return
            chosen = lectures[subj][idx]
            user_lecture[uid] = chosen
            await callback.message.answer(
                f"Лекція: {chosen}\nМожеш ставити запитання по цій лекції."
            )
            await callback.answer()
            return

        await callback.answer()
