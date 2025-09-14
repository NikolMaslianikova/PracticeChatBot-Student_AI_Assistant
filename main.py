import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import ollama
import os
from dotenv import load_dotenv
from logs import log_user_message, log_bot_answer, log_error
from prompts import SUBJECT_READABLE, SYSTEM_PROMPT_BASE, PRESET_PROMPTS, GOODBYE_WORDS
from user_data import user_lecture, user_style, user_subject
from commands import func_commands
from callbacks import func_callbacks
from rag import build_rag_prompt

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME")

bot = Bot(token=TOKEN)
dp = Dispatcher()

func_commands(dp)
func_callbacks(dp)

def build_system_prompt(user_id: int) -> str:
    subj_code = user_subject.get(user_id)
    style_key = user_style.get(user_id)
    lecture_title = user_lecture.get(user_id)

    subject_txt = SUBJECT_READABLE.get(subj_code, "—")
    style_txt = PRESET_PROMPTS.get(style_key, "Відповідай просто і зрозуміло.")
    lecture_txt = lecture_title or "Не вибрано"

    return SYSTEM_PROMPT_BASE.format(subject=subject_txt, style=style_txt, lecture=lecture_txt)

async def ollama_chat_async(model: str, system_prompt: str, user_text: str) -> str:
    def _call():
        return ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            options={"temperature": 0.2, "top_p": 0.9},
        )
    resp = await asyncio.to_thread(_call)
    return resp["message"]["content"]

@dp.message()
async def on_user_message(message: Message):
    uid = message.from_user.id
    user_text = (message.text or "").lower().strip()

    if uid not in user_subject and uid not in user_style and uid not in user_lecture:
        await message.answer("Сесію завершено. Почати нову → /start")
        return

    if any(word in user_text for word in GOODBYE_WORDS):
        await message.answer("Дякую за розмову! Якщо потрібна допомога — пиши.")
        return

    if uid not in user_subject:
        await message.answer("Спочатку обери предмет: /start"); return
    if uid not in user_style:
        await message.answer("Спочатку обери стиль: /style"); return
    if uid not in user_lecture:
        await message.answer("Спочатку обери лекцію: /lectures"); return

    system_prompt = build_system_prompt(uid)
    rag_prompt = build_rag_prompt(uid, user_text)

    await log_user_message(uid, user_text, {
        "subject": SUBJECT_READABLE.get(user_subject[uid]),
        "style": user_style[uid],
        "lecture": user_lecture[uid]
    })

    thinking_msg = await message.answer("Думаю над відповіддю...")
    typing_task = asyncio.create_task(show_typing(message.chat))

    try:
        answer = await ollama_chat_async(MODEL_NAME, system_prompt, rag_prompt)

        typing_task.cancel()

        await log_bot_answer(uid, answer, {
            "subject": SUBJECT_READABLE.get(user_subject[uid]),
            "style": user_style[uid],
            "lecture": user_lecture[uid]
        })

        for i in range(0, len(answer), 3500):
            await message.answer(answer[i:i+3500])

    except Exception as e:
        typing_task.cancel()
        await thinking_msg.edit_text(
            "Не вдалось звернутись до локальної моделі.\n"
            "Перевір, що Ollama запущений і модель встановлена.\n"
            "Приклади в терміналі:\n"
            "  ollama list\n"
            "  ollama pull gemma3:4b\n"
            "  ollama run gemma3:4b \"hello\""
        )
        await log_error(uid, str(e), {
            "subject": SUBJECT_READABLE.get(user_subject.get(uid)),
            "style": user_style.get(uid),
            "lecture": user_lecture.get(uid)
        })

async def show_typing(chat: types.Chat):
    try:
        while True:
            await chat.do("typing")
            await asyncio.sleep(3)
    except asyncio.CancelledError:
        pass

async def main():
    print("Бот запущений")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
