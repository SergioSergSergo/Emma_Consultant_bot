from aiogram import Router
from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
import re

from app.questionnaire.data import FeedbackQuestions, Questions
from app.states import Questionnaire, Feedback
from app.handlers.command_classes import BotCommandItem
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.questionnaire.confirmation_handler import provide_calendly


router = Router(name='commands')

COMMANDS = [
    BotCommandItem(
        key="start",
        command="/start",
        short_desc="Почати бот",
        long_desc="Почати бот та побачити привітальне повідомлення",
        access="always"
    ),
    BotCommandItem(
        key="help",
        command="/help",
        short_desc="Довідка",
        long_desc="Показує довідкове повідомлення",
        access="always"
    ),
    BotCommandItem(
        key="restart",
        command="/restart_questionnaire",
        short_desc="розпочати опитування спочатку",
        long_desc="Обнуляє дані і повертає до першого питання анкети",
        access="always"
    ),
]

# Стартова клавіатура

# Обробка вибору користувача
@router.message(Questionnaire.CALLENDLY, F.text)
async def choose_brief(message: Message, state: FSMContext):
    if message.text == "Заповнити бриф зараз":
        await message.answer(
            Questions.NAME, parse_mode="Markdown", reply_markup=None
        )
        await state.set_state(Questionnaire.NAME)
    elif message.text == "Заповнити бриф пізніше":
        await provide_calendly(message, state)  # одразу показуємо кнопку Calendly
    else:
        await message.answer("Будь ласка, оберіть одну з доступних опцій.")


@router.callback_query(F.data.in_({"brief_now", "brief_later"}))
async def handle_brief_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()  # закриває "loading" у Telegram

    if callback.data == "brief_now":
        await callback.message.answer(
            Questions.NAME, parse_mode="Markdown", reply_markup=None
        )
        await state.set_state(Questionnaire.NAME)

    elif callback.data == "brief_later":
        # Відправляємо Calendly
        await provide_calendly(callback.message, state)

        # Додаємо кнопку для проходження брифу після зустрічі
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Заповнити бриф після зустрічі",
                    callback_data="brief_after_meeting"
                )]
            ]
        )
        await callback.message.answer(
            "Якщо бажаєте, ви можете заповнити бриф після зустрічі:",
            reply_markup=kb
        )
        await state.set_state(Questionnaire.CALLENDLY)


@router.callback_query(F.data == "brief_after_meeting")
async def handle_brief_after_meeting(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        Questions.NAME, parse_mode="Markdown", reply_markup=None
    )
    await state.set_state(Questionnaire.NAME)



START_BRIEF_INLINE_KB = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Заповнити бриф зараз", callback_data="brief_now")
        ],
        [
            InlineKeyboardButton(text="Заповнити бриф пізніше", callback_data="brief_later")
        ],
        [
            InlineKeyboardButton(text="Відгук про зустріч", callback_data="brief_feedback")
        ]

    ]
)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Старт опитування з вибором дії через Inline кнопки"""
    await state.clear()  # очищаємо попередні дані

    user = message.from_user
    await message.answer(
        f"Вітаю, <b>{user.first_name or 'шановний користувачу'}</b>! 👋\n\n"
        "Я — бот команди <b>EMMA Consulting</b> і допоможу підготувати базову інформацію перед вашою зустріччю з фінансовим експертом.\n\n"
        "Щоб скоротити час консультації, ми пропонуємо заповнити короткий бриф. Ви можете:\n"
        "• Заповнити бриф <b>зараз</b> — я поставлю кілька простих питань.\n"
        "• Заповнити бриф <b>пізніше</b> — обрати зручний час для зустрічі через Calendly 📅.\n"
        "• Надати відгук про зустріч.\n\n"
        "ℹ️ Також ви завжди можете:\n"
        "• почати опитування заново — командою /restart_questionnaire\n"
        "• перезапустити бота — командою /start\n"
        "• отримати довідку — командою /help",
        parse_mode="HTML",
        reply_markup=START_BRIEF_INLINE_KB,  # кнопки під текстом
    )

    await state.set_state(Questionnaire.CALLENDLY)


def escape_md(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Довідка"""
    text = (
        "💡 Довідка по боту EMMA Consulting\n\n"
        "Цей бот допоможе вам пройти опитування і забронювати зустріч з фінансовим експертом.\n\n"
        "Основні команди:\n"
        "• /start — почати спілкування з ботом\n"
        "• /restart_questionnaire — почати опитування заново\n"
        "• /help — показати це повідомлення\n\n"
    )

    await message.answer(
        escape_md(text),
        parse_mode="MarkdownV2"
    )


@router.message(Command("restart_questionnaire"))
async def cmd_restart(message: Message, state: FSMContext):
    """Почати опитування заново"""
    await state.clear()

    await message.answer(
        "🔄 Ви розпочали анкету спочатку.\n\n"
        f"{Questions.NAME}",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

    await state.set_state(Questionnaire.NAME)
    
@router.callback_query(F.data == "brief_feedback")
async def start_feedback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    # Перше повідомлення — привітання
    await callback.message.answer(
        "💬 Давайте залишимо короткий відгук.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

    # Друге повідомлення — питання про ім'я
    await callback.message.answer(
        FeedbackQuestions.NAME,
        parse_mode="Markdown",
    )

    await state.set_state(Feedback.NAME)
