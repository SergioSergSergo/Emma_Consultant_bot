# ======== ВІДГУК ПРО ЗУСТРІЧ =========
from email import header
from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from app.data.text_classes import FeedbackQuestions, escape_md
from app.states import Feedback
from app.config import GROUP_CHAT_ID  # імпортуйте константу з ID групи
from app.data.text_classes import build_feedback_summary
router = Router(name='feedback')


@router.message(Feedback.NAME)
async def feedback_name(message: Message, state: FSMContext):
    await state.update_data(NAME=message.text.strip())
    await message.answer(FeedbackQuestions.Q1)
    await state.set_state(Feedback.Q1)


@router.message(Feedback.Q1)
async def feedback_q1(message: Message, state: FSMContext):
    await state.update_data(q1=message.text)
    await message.answer(FeedbackQuestions.Q2)
    await state.set_state(Feedback.Q2)


@router.message(Feedback.Q2)
async def feedback_q2(message: Message, state: FSMContext):
    await state.update_data(q2=message.text)

    scale_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(i), callback_data=f"rate_{i}") for i in range(0, 6)],
            [InlineKeyboardButton(text=str(i), callback_data=f"rate_{i}") for i in range(6, 11)],
        ]
    )
    await message.answer(FeedbackQuestions.Q3, reply_markup=scale_kb)
    await state.set_state(Feedback.Q3)


@router.callback_query(F.data.startswith("rate_"))
async def feedback_q3(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split("_")[1])
    await state.update_data(q3=rating)
    await callback.answer(f"Ви обрали {rating}")

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Instagram")],
            [KeyboardButton(text="Рекомендація партнера/колеги")],
            [KeyboardButton(text="Бізнес-клуб")],
            [KeyboardButton(text="Пошук Google")],
            [KeyboardButton(text="Інше")],
        ],
        resize_keyboard=True
    )

    await callback.message.answer(FeedbackQuestions.Q4, reply_markup=kb)
    await state.set_state(Feedback.Q4)


@router.message(Feedback.Q4)
async def feedback_q4(message: Message, state: FSMContext):
    await state.update_data(q4=message.text)
    data = await state.get_data()
    # Формуємо шапку зовні
    header = f"Ім'я: {data.get('NAME', '—')}\n\n"
    feedback_text = build_feedback_summary(data)

    confirm_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Так"), KeyboardButton(text="Ні")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    user_summary_text = header + feedback_text
    await message.answer(
        f"{user_summary_text}\n\nВсе вірно?",
        reply_markup=confirm_kb,
        parse_mode="Markdown"
    )
    await state.set_state(Feedback.DONE)


@router.message(Feedback.DONE, F.text)
async def feedback_confirm(message: Message, state: FSMContext):
    user_answer = message.text.strip().lower()
    data = await state.get_data()  # беремо дані із state

    if user_answer in ["так", "yes"]:
    
        # Формуємо шапку зовні
        user_name = escape_md(message.from_user.full_name or "Інформація недоступна")
        user_nickname = escape_md(f"@{message.from_user.username}" if message.from_user.username else "Користувач без username")
        name = escape_md(data.get("NAME", "—"))

        header = f"📬 Новий відгук від {user_name} ({user_nickname}):\n\n"
        header += f"Ім'я: {name}\n\n"

        # Генеруємо текст фідбеку без шапки
        text = header + build_feedback_summary(data)
        await message.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=text,
            parse_mode="Markdown"
        )
        await message.answer(
            "✅ Дякуємо за ваш відгук! Він дуже важливий для нас 💙",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    else:
        await message.answer(
            "Якщо хочете заповнити відгук ще раз — натисніть /start",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
