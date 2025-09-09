import asyncio
from typing import Dict
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
import ollama

TOKEN = "unknown"
MODEL_NAME = "unknown"

bot = Bot(token=TOKEN)
dp = Dispatcher()

SUBJECT_READABLE = {"do": "ДО (Дослідження операцій)", "networks": "Комп’ютерні мережі"}

PRESET_PROMPTS = {
    "short": "Відповідай максимально коротко і додавай 1 приклад.",
    "detailed_step": (
        "Відповідай більш детально, крок за кроком. "
        "Для кожного кроку давай короткий заголовок, пояснення, формули або псевдокод, приклад і потенційні помилки. "
        "Наприкінці — короткий висновок та рекомендації."
    ),
    "detailed_analysis": (
        "Пояснюй дуже детально й аналітично: дай детальний опис, потім альтернативні підходи з порівнянням (плюси/мінуси), "
        "оцінку складності та часу, покрокову реалізацію і приклади коду/розрахунків. Вказуй потенційні помилки."
        "Наприкінці — короткий висновок та рекомендації."
    )
}

lectures = {
    "do": [
        "Лекція 1: Вступ у дослідження операцій",
        "Лекція 2: Лінійне програмування",
        "Лекція 3: Симплекс метод розв’язання задачі лінійного програмування",
        "Лекція 4: Двоїстість у задачах лінійного програмування",
        "Лекція 5: Транспортна задача",
        "Лекція 6: Задачі дискретного програмування",
        "Лекція 7: Методи одновимірної оптимізації",
        "Лекція 8: Нелінійне програмування",
        "Лекція 9: Опукле та квадратичне програмування",
        "Лекція 10: Нелінійне програмування. Методи безумовної оптимізації",
        "Лекція 11: Нелінійне програмування. Методи умовної оптимізації",
        "Лекція 12: Динамічне програмування",
        "Лекція 13: Нелінійне програмування з сепарабельними функціями. Дробово-лінійне програмування",
        "Лекція 14: Чисельні методи розв’язання багатовимірних задач нелінійного програмування за наявності обмежень"
    ],
    "networks": [
        "Лекція 1: Вступ у компʼютерні мережі",
        "Лекція 2: PHY",
        "Лекція 3: DataLink",
        "Лекція 4: MAC",
        "Лекція 5: Ethernet",
        "Лекція 6: WiFi",
        "Лекція 7: Routing",
        "Лекція 8: Internetworking",
        "Лекція 9: IP",
        "Лекція 10: ICMP ARP DHCP",
        "Лекція 11: Transport",
        "Лекція 12: TCP UDP",
        "Лекція 13: DNS EMAIL",
        "Лекція 14: HTTP",
        "Лекція 15: WebAppSec"
    ]
}

SYSTEM_PROMPT_BASE = """
Ти — навчальний помічник для студентів.
Допомагай студентам зі спеціальності "Штучний інтелект".
Відповідай українською, зрозуміло й коректно, структуровано (списки/кроки),
з прикладами за потреби, опираючись на матеріали курсу.
Якщо питання нечітке — коротко уточни.

Предмет: {subject}
Стиль відповіді: {style}
Лекція: {lecture}
"""

user_subject: Dict[int, str] = {}
user_style: Dict[int, str] = {}
user_lecture: Dict[int, str] = {}

def subject_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ДО", callback_data="subj:do")],
        [InlineKeyboardButton(text="Комп'ютерні мережі", callback_data="subj:networks")]
    ])

def style_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Коротко + приклад", callback_data="style:short")],
        [InlineKeyboardButton(text="Детально, кроки", callback_data="style:detailed_step")],
        [InlineKeyboardButton(text="Глибоко-аналітично", callback_data="style:detailed_analysis")],
    ])

def lectures_kb(subject: str) -> InlineKeyboardMarkup:
    rows = []
    for idx, lec in enumerate(lectures[subject], start=1):
        rows.append([InlineKeyboardButton(text=lec, callback_data=f"lec:{subject}:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

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

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! 👩‍💻 Я твій навчальний помічник.\n"
        "Обери предмет, з яким ми будемо працювати:",
        reply_markup=subject_kb()
    )

@dp.message(Command("status"))
async def cmd_status(message: Message):
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
async def cmd_subject(message: Message):
    await message.answer("Обери предмет:", reply_markup=subject_kb())

@dp.message(Command("style"))
async def cmd_style(message: Message):
    if message.from_user.id not in user_subject:
        await message.answer("Спочатку обери предмет: /start"); return
    await message.answer("Обери стиль відповіді:", reply_markup=style_kb())

@dp.message(Command("lectures"))
async def cmd_lectures(message: Message):
    uid = message.from_user.id
    if uid not in user_subject:
        await message.answer("Спочатку обери предмет: /start"); return
    if uid not in user_style:
        await message.answer("Спочатку обери стиль відповіді: /style"); return
    await message.answer("Обери лекцію:", reply_markup=lectures_kb(user_subject[uid]))


@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    data = callback.data or ""
    uid = callback.from_user.id

    if data.startswith("subj:"):
        subj = data.split(":")[1]
        if subj not in lectures:
            await callback.answer("Невідомий предмет", show_alert=True); return
        user_subject[uid] = subj
        user_style.pop(uid, None)
        user_lecture.pop(uid, None)
        await callback.message.answer(
            f"Предмет: {SUBJECT_READABLE[subj]}\nОбери стиль відповіді:",
            reply_markup=style_kb()
        )
        await callback.answer(); return

    if data.startswith("style:"):
        style_key = data.split(":")[1]
        if style_key not in PRESET_PROMPTS:
            await callback.answer("Невідомий стиль", show_alert=True); return
        user_style[uid] = style_key
        await callback.message.answer(
            "Стиль обрано.\nОбери лекцію:",
            reply_markup=lectures_kb(user_subject[uid])
        )
        await callback.answer(); return

    if data.startswith("lec:"):
        _, subj, idx_str = data.split(":")
        idx = int(idx_str) - 1
        if subj not in lectures or idx < 0 or idx >= len(lectures[subj]):
            await callback.answer("Некоректна лекція", show_alert=True); return
        chosen = lectures[subj][idx]
        user_lecture[uid] = chosen
        await callback.message.answer(
            f"Лекція: {chosen}\nМожеш ставити запитання по цій лекції."
        )
        await callback.answer(); return

    await callback.answer()

#user's message
@dp.message()
async def on_user_message(message: Message):
    uid = message.from_user.id
    if uid not in user_subject:
        await message.answer("Спочатку обери предмет: /start"); return
    if uid not in user_style:
        await message.answer("Спочатку обери стиль: /style"); return
    if uid not in user_lecture:
        await message.answer("Спочатку обери лекцію: /lectures"); return

    system_prompt = build_system_prompt(uid)
    user_text = message.text or ""

    try:
        await message.chat.do("typing")
        answer = await ollama_chat_async(MODEL_NAME, system_prompt, user_text)
        for i in range(0, len(answer), 3500):
            await message.answer(answer[i:i+3500])
    except Exception as e:
        await message.answer(
            "Не вдалось звернутись до локальної моделі.\n"
            "Перевір, що Ollama запущений і модель встановлена.\n"
            "Приклади в терміналі:\n"
            "  ollama list\n  ollama pull gemma3:4b\n  ollama run gemma3:4b \"hello\""
        )
        print("Ollama error:", e)

async def main():
    print("Бот запущений")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
