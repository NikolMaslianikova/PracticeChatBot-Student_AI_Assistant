from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from prompts import lectures

def subject_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ДО", callback_data="subj:do")],
        [InlineKeyboardButton(text="Комп'ютерні мережі", callback_data="subj:networks")]
    ])

def style_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Коротко + приклад", callback_data="style:short")],
        [InlineKeyboardButton(text="Детально, кроки", callback_data="style:detailed_step")],
        [InlineKeyboardButton(text="Глибоко-аналітично", callback_data="style:detailed_analysis")],
    ])

def lectures_kb(subject: str):
    rows = []
    for idx, lec in enumerate(lectures[subject], start=1):
        rows.append([InlineKeyboardButton(text=lec, callback_data=f"lec:{subject}:{idx}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
