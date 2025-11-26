# handlers/questionnaire.py
from aiogram import Router, F
from aiogram.types import Message,  ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import  InlineKeyboardButton, InlineKeyboardMarkup

from app.states import Questionnaire
from app.data.text_classes import Questions, build_summary, escape_md
from app.config import  GROUP_CHAT_ID
from app.config import CALENDLY_URL
from app.data.keyboards import CONTACT_INLINE, EMPLOYEES, LEGAL_FORM, YES_NO, FORMAT, REFERRAL
from app.handlers.user_cmnds import send_start_message
router = Router(name="questionnaire")

# Початок анкети
@router.callback_query(F.data == "fill_brief")
async def start_questionnaire(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        Questions.NAME,
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Questionnaire.NAME)

# 1. Ім'я
@router.message(Questionnaire.NAME, F.text)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(NAME=message.text)
    await message.answer(Questions.PHONE)
    await state.set_state(Questionnaire.PHONE)

# 2. Телефон 
@router.message(Questionnaire.PHONE)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(PHONE=phone)
    await message.answer(Questions.BUSINESS)
    await state.set_state(Questionnaire.BUSINESS)

# 3. Бізнес
@router.message(Questionnaire.BUSINESS, F.text)
async def get_business(message: Message, state: FSMContext):
    await state.update_data(BUSINESS=message.text)
    await message.answer(Questions.WEBSITE)
    await state.set_state(Questionnaire.WEBSITE)

# 4. Вебсайт
@router.message(Questionnaire.WEBSITE, F.text)
async def get_website(message: Message, state: FSMContext):
    await state.update_data(WEBSITE=message.text)
    await message.answer(Questions.EMPLOYEES, reply_markup=EMPLOYEES)
    await state.set_state(Questionnaire.EMPLOYEES) 

# 5. Працівники
@router.message(Questionnaire.EMPLOYEES, F.text)
async def get_employees(message: Message, state: FSMContext):
    await state.update_data(EMPLOYEES=message.text)
    await message.answer(Questions.LEGAL_FORM, reply_markup=LEGAL_FORM)
    await state.set_state(Questionnaire.LEGAL_FORM)

# 6. Юридична форма
@router.message(Questionnaire.LEGAL_FORM, F.text)
async def get_legal_form(message: Message, state: FSMContext):
    await state.update_data(LEGAL_FORM=message.text)
    await message.answer(Questions.ROLES, reply_markup=ReplyKeyboardRemove())
    await state.set_state(Questionnaire.ROLES)

# 7. Ролі у бізнесі
@router.message(Questionnaire.ROLES, F.text)
async def get_roles(message: Message, state: FSMContext):
    await state.update_data(ROLES=message.text)
    await message.answer(Questions.FIN_KNOWLEDGE, reply_markup=YES_NO)
    await state.set_state(Questionnaire.FIN_KNOWLEDGE)

# 8. Фінансова грамотність
@router.message(Questionnaire.FIN_KNOWLEDGE, F.text)
async def get_fin_knowledge(message: Message, state: FSMContext):
    await state.update_data(FIN_KNOWLEDGE=message.text)
    await message.answer(Questions.FIN_PERSON, reply_markup=ReplyKeyboardRemove())
    await state.set_state(Questionnaire.FIN_PERSON)

# 9. Відповідальний за фінанси
@router.message(Questionnaire.FIN_PERSON, F.text)
async def get_fin_person(message: Message, state: FSMContext):
    await state.update_data(FIN_PERSON=message.text)
    await message.answer(Questions.FIN_REPORTS)
    await state.set_state(Questionnaire.FIN_REPORTS)

# 10. Фінансова звітність
@router.message(Questionnaire.FIN_REPORTS, F.text)
async def get_fin_reports(message: Message, state: FSMContext):
    await state.update_data(FIN_REPORTS=message.text)
    await message.answer(Questions.CRM, reply_markup=YES_NO)
    await state.set_state(Questionnaire.CRM)

# 11. CRM
@router.message(Questionnaire.CRM, F.text)
async def get_crm(message: Message, state: FSMContext):
    await state.update_data(CRM=message.text)
    if message.text == "Так":
        await message.answer(Questions.CRM_NAME)
        await state.set_state(Questionnaire.CRM_NAME)
    else:
        await state.update_data(CRM_NAME="Ні")
        await get_crm_name(message, state)

# 12. Назва CRM
@router.message(Questionnaire.CRM_NAME, F.text)
async def get_crm_name(message: Message, state: FSMContext):
    if message.text != "Ні":
        await state.update_data(CRM_NAME=message.text)

    await message.answer(Questions.FINMAP, reply_markup=YES_NO)
    await state.set_state(Questionnaire.FINMAP)

# 13. Finmap
@router.message(Questionnaire.FINMAP, F.text)
async def get_finmap(message: Message, state: FSMContext):
    await state.update_data(FINMAP=message.text)
    await message.answer(Questions.GOOGLE_SHEETS, reply_markup=YES_NO)
    await state.set_state(Questionnaire.GOOGLE_SHEETS)

# 14. Google Таблиці
@router.message(Questionnaire.GOOGLE_SHEETS, F.text)
async def get_google_sheets(message: Message, state: FSMContext):
    await state.update_data(GOOGLE_SHEETS=message.text)
    await message.answer(Questions.MEETINGS, reply_markup=YES_NO)
    await state.set_state(Questionnaire.MEETINGS)

# 15. Наради
@router.message(Questionnaire.MEETINGS, F.text)
async def get_meetings(message: Message, state: FSMContext):
    await state.update_data(MEETINGS=message.text)

    if message.text == "Так":
        await message.answer(Questions.MEETING_DETAILS)
        await state.set_state(Questionnaire.MEETING_DETAILS)
    else:
        await state.update_data(MEETING_DETAILS="Немає")
        await get_meeting_details(message, state)

# 16. Деталі нарад
@router.message(Questionnaire.MEETING_DETAILS, F.text)
async def get_meeting_details(message: Message, state: FSMContext):
    if message.text != "Немає":
        await state.update_data(MEETING_DETAILS=message.text)

    await message.answer(Questions.REQUESTS)
    await state.set_state(Questionnaire.REQUESTS)

# 17. Запити
@router.message(Questionnaire.REQUESTS, F.text)
async def get_requests(message: Message, state: FSMContext):
    await state.update_data(REQUESTS=message.text)
    await message.answer(Questions.USED_CONSULTANTS, reply_markup=YES_NO)
    await state.set_state(Questionnaire.USED_CONSULTANTS)

# 18. Використання консультантів
@router.message(Questionnaire.USED_CONSULTANTS, F.text)
async def get_used_consultants(message: Message, state: FSMContext):
    await state.update_data(USED_CONSULTANTS=message.text)

    await message.answer(Questions.FORMAT, reply_markup=FORMAT)
    await state.set_state(Questionnaire.FORMAT)

# 19. Формат консультації
@router.message(Questionnaire.FORMAT, F.text)
async def get_format(message: Message, state: FSMContext):
    await state.update_data(FORMAT=message.text)
    await message.answer(Questions.REFERRAL, reply_markup=REFERRAL)
    await state.set_state(Questionnaire.REFERRAL)


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

        await message.answer("✅ Дякуємо! Анкета збережена.", reply_markup=ReplyKeyboardRemove())

        await state.clear()
        await send_start_message(message, state)

        
    else:
        await message.answer(
            "Добре, давайте почнемо спочатку. Введіть /restart_questionnaire"
        )
        # залишаємо стан CONFIRM
