from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from app.states import Questionnaire
from app.questionnaire.data import Questions, build_summary, escape_md
from app.questionnaire.keyboards import YES_NO
from app.config import  GROUP_CHAT_ID
from app.config import CALENDLY_URL
router = Router(name="confirmation_handler")

# 20. Джерело інформації
@router.message(Questionnaire.REFERRAL, F.text)
async def get_referral(message: Message, state: FSMContext):
    await state.update_data(REFERRAL=message.text)

    data = await state.get_data()
    summary = build_summary(data)

    await message.answer(
        f"*{Questions.CONFIRM}*\n\n{summary}\n\nВсе правильно?",
        parse_mode="Markdown",
        reply_markup=YES_NO
    )
    await state.set_state(Questionnaire.CONFIRM)

@router.message(Questionnaire.CONFIRM, F.text)
async def get_confirm(message: Message, state: FSMContext):
    user_answer = message.text.lower()
    await state.update_data(CONFIRM=user_answer)

    data = await state.get_data()
    summary = build_summary(data)  # формуємо актуальний текст підсумку

    if user_answer in ["так", "yes"]:
        # Формуємо текст з ім'ям користувача та його Telegram ID
        # Формуємо шапку зовні
        user_name = escape_md(message.from_user.full_name or "Інформація недоступна")
        user_nickname = escape_md(f"@{message.from_user.username}" if message.from_user.username else "Користувач без username")
        name = escape_md(data.get("NAME", "—"))

        header = f"📬 Нова анкета від {user_name} ({user_nickname}):\n\n"
        header += f"Ім'я: {name}\n\n"

        # Генеруємо текст фідбеку без шапки
        text = header + build_summary(data)

        await message.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=text,
            parse_mode="Markdown"
        )

        await message.answer("✅ Дякуємо! Анкета збережена.")
        await provide_calendly(message, state)
    else:
        await message.answer(
            "Добре, давайте почнемо спочатку. Введіть /restart_questionnaire"
        )
        # залишаємо стан CONFIRM

async def provide_calendly(message: Message, state: FSMContext):
    keyboard = [
        [InlineKeyboardButton(text="📅 Забронювати зустріч", url=CALENDLY_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(
        "Натисніть кнопку, щоб обрати зручний час:",
        reply_markup=reply_markup
    )
    await state.clear()  # очищаємо стан користувача
