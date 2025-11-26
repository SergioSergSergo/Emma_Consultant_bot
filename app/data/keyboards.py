from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from app.config import CALENDLY_URL

btn_choose_meeting_time = InlineKeyboardButton(
    text="📅 Обрати час зустрічі",
    url=CALENDLY_URL
)

btn_fill_brief = InlineKeyboardButton(
    text="📝 Заповнити бриф",
    callback_data="fill_brief"
)

btn_feedback = InlineKeyboardButton(
    text="⭐ Надати відгук про зустріч",
    callback_data="give_feedback"
)

START_BRIEF_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
      [btn_choose_meeting_time],
      [btn_fill_brief],
        [btn_feedback]
    ]
)

# --- Кількість працівників ---
EMPLOYEES = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Соло-підприємець")],
        [KeyboardButton(text="До 5-ти працівників")],
        [KeyboardButton(text="До 10-ти")],
        [KeyboardButton(text="До 50-ти")],
        [KeyboardButton(text="Більше 50-ти")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# --- Юридична форма ---
LEGAL_FORM = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ФОП")],
        [KeyboardButton(text="ТЗОВ")],
        [KeyboardButton(text="Інше")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# --- Так / Ні ---
YES_NO = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Так")],
        [KeyboardButton(text="Ні")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# --- Формат консультації ---
FORMAT = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Offline у Львові")],
        [KeyboardButton(text="Online Zoom/Google Meet")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# --- Джерело інформації про вас ---
REFERRAL = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Instagram")],
        [KeyboardButton(text="Порада одноклубника")],
        [KeyboardButton(text="Порада друга/подруги")],
        [KeyboardButton(text="Google пошук")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# --- Inline кнопка Calendly ---
def calendly(url: str) -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(text="📅 Забронювати зустріч", url=url)]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



# --- Контакт ---
CONTACT = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📞 Поділитися номером телефону", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

CONTACT_INLINE = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📞 Поділитися номером телефону", callback_data="share_phone")]
    ]
)