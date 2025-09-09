from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import asyncio

TOKEN = "uknown"

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
        "Лекція 8: Internetworking ",
        "Лекція 9: IP",
        "Лекція 10: ICMP ARP DHCP",
        "Лекція 11: Transport",
        "Лекція 12: TCP UDP",
        "Лекція 13: DNS EMAIL",
        "Лекція 14: HTTP",
        "Лекція 15: WebAppSec"
    ]
}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = [
        [InlineKeyboardButton(text="ДО", callback_data="do")],
        [InlineKeyboardButton(text="Комп'ютерні мережі", callback_data="networks")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        "Привіт! 👩‍💻 Я твій навчальний помічник.\n"
        "Обери предмет, з яким ми будемо працювати:",
        reply_markup=reply_markup
    )

@dp.callback_query()
async def process_subject(callback: types.CallbackQuery):
    subject = callback.data

    if subject in lectures:
        keyboard = [
            [InlineKeyboardButton(text=lec, callback_data=f"{subject}_{i}")]
            for i, lec in enumerate(lectures[subject], start=1)
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

        await callback.message.answer(
            f"Ти обрав: { 'ДО' if subject == 'do' else 'Комп’ютерні мережі' }\n\n"
            "Обери лекцію:",
            reply_markup=reply_markup
        )
    else:
        await callback.message.answer("Невідомий предмет")

    await callback.answer()

@dp.callback_query()
async def process_lecture(callback: types.CallbackQuery):
    data = callback.data.split("_")
    if len(data) == 2:
        subject, lecture_id = data
        if subject in lectures:
            lecture_title = lectures[subject][int(lecture_id) - 1]
            await callback.message.answer(f"Ти обрав: {lecture_title}\n\n(текст із PDF)")
    await callback.answer()

async def main():
    print("Бот запущений")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
