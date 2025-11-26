from aiogram import Router
from aiogram import F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import re
from app.data.keyboards import START_BRIEF_INLINE_KB
from app.data.text_classes import FeedbackQuestions, Questions
from app.states import Questionnaire, Feedback


router = Router(name='commands')
# Стартова клавіатура

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await send_start_message(message, state)


async def send_start_message(message: Message, state: FSMContext):
    """Старт опитування з вибором дії через Inline кнопки"""
    await state.clear()  # очищаємо попередні дані

    user = message.from_user
    await message.answer(
        f"Вітаю, <b>{user.first_name or 'шановний користувачу'}</b>! 👋\n\n"
        "Я — бот команди <b>Emma Consults</b> і допоможу підготувати базову інформацію перед вашою зустріччю з фінансовим експертом.\n\n"
        "Щоб підвищити ефективність сесії, я пропоную заповнити <b>короткий бриф</b>.\n\n"
        "Ви можете обрати один із варіантів:\n"
        "• 📅 <b>Запланувати зустріч</b> у зручний для вас час через Calendly.\n"
        "• 📝 <b>Заповнити бриф</b> — я поставлю кілька простих запитань.\n"
        "• ⭐ <b>Залишити відгук</b> про зустріч.\n\n"
        "ℹ️ Ви завжди можете перезапустити бот командою /start\n",
        parse_mode="HTML",
        reply_markup=START_BRIEF_INLINE_KB,
    )
    await state.set_state(Questionnaire.CALLENDLY)


def escape_md(text: str) -> str:
    return re.sub(r'([_*\[\]()~`>#+\-=|{}!])', r'\\\1', text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Довідка"""
    text = (
        "💡 Довідка по боту EMMA Consulting\n\n"
        "Цей бот допоможе вам пройти опитування і забронювати зустріч з фінансовим експертом.\n\n"
        "Основні команди:\n"
        "• /start — почати спілкування з ботом\n"
        "• /restart_questionnaire — почати опитування заново\n"
    )
    await message.answer( escape_md(text), parse_mode="MarkdownV2")


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





'''
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
                    text="Заповнити бриф",
                    callback_data="brief_after_meeting"
                )]
            ]
        )
        await callback.message.answer(
        "Щоб найкраще підготуватися до запланованої зустрічі, заповніть, будь ласка, **короткий бриф**:",
        reply_markup=kb, parse_mode="Markdown" )
        await state.set_state(Questionnaire.CALLENDLY)


@router.callback_query(F.data == "brief_after_meeting")
async def handle_brief_after_meeting(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        Questions.NAME, parse_mode="Markdown", reply_markup=None
    )
    await state.set_state(Questionnaire.NAME)

'''