from enum import Enum, auto
import re
class Questions:
    NAME = "Як я можу до вас звертатися?"
    PHONE = "Особистий номер телефону:"
    BUSINESS = "Короткий опис вашого поточного або  майбутнього бізнесу (назва, ніша, рік заснування):"
    WEBSITE = "Сайт та соцмережі вашого бізнесу:"
    EMPLOYEES = "Кількість працівників:"
    LEGAL_FORM = "Форма діяльності:"
    ROLES = "Які ролі ви виконуєте в бізнесі?"
    FIN_KNOWLEDGE = "Чи розумієте ви різницю між P&L та Cash Flow?"
    FIN_PERSON = "Хто з команди займається фінансовим аналізом?"
    FIN_REPORTS = "Які фінансові звіти та показники відслідковуються станом на сьогодні?"
    CRM = "Чи користуєтесь CRM системою?"
    CRM_NAME = "Якщо так, то якою CRM користуєтесь?"
    FINMAP = "Чи користуєтесь додатком Finmap?"
    GOOGLE_SHEETS = "Чи ведете фінансовий облік у Google Таблицях?"
    MEETINGS = "Чи сформований графік нарад із командою?"
    MEETING_DETAILS = "В яких ключових нарадах приймаєте участь?"
    REQUESTS = "Детально опишіть запити, які спонукали вас звернутись по консультацію/аудит/фін.модель:"
    USED_CONSULTANTS = "Чи користувались ви раніше послугами фінансових консультантів?"
    FORMAT = "Бажаний формат проведення зустрічі:"
    REFERRAL = "Як ви дізнались про мене?"
    CONFIRM = "Перевірте свої відповіді"

class FeedbackQuestions:
    NAME = "Ваше ім’я і прізвище:"
    PHONE = "Ваш номер телефону (для зворотного зв’язку):"
    Q1 = "Що вам найбільше сподобалося у нашій співпраці?"
    Q2 = "Що можна було б покращити, щоб результат був ще ціннішим?"
    Q3 = "Наскільки ймовірно, що ви порекомендуєте мене або мої послуги своїм колегам (0–10):"
    Q4 = "Як ви про мене дізнались?"


def escape_md(text: str) -> str:
    """Екранує спеціальні символи MarkdownV2, крім дефіса '-'"""
    # Усі символи MarkdownV2, окрім дефіса
    return re.sub(r'([_*[\]()~`>#+=|{}.!])', r'\\\1', text)


def build_summary_lines(data: dict, fields: list) -> str:
    summary_lines = []
    for i, (question, key) in enumerate(fields, start=1):
        answer = escape_md(str(data.get(key, "—")))  # екрануємо тільки answer
        summary_lines.append(f"{i}. *{question}*\n→ `{answer}`")
    return "\n".join(summary_lines)


def build_summary(user_data: dict) -> str:
    fields = [
        (Questions.BUSINESS, "BUSINESS"),
        (Questions.WEBSITE, "WEBSITE"),
        (Questions.EMPLOYEES, "EMPLOYEES"),
        (Questions.LEGAL_FORM, "LEGAL_FORM"),
        (Questions.ROLES, "ROLES"),
        (Questions.FIN_KNOWLEDGE, "FIN_KNOWLEDGE"),
        (Questions.FIN_PERSON, "FIN_PERSON"),
        (Questions.FIN_REPORTS, "FIN_REPORTS"),
        (Questions.CRM, "CRM"),
        (Questions.CRM_NAME, "CRM_NAME"),
        (Questions.FINMAP, "FINMAP"),
        (Questions.GOOGLE_SHEETS, "GOOGLE_SHEETS"),
        (Questions.MEETINGS, "MEETINGS"),
        (Questions.MEETING_DETAILS, "MEETING_DETAILS"),
        (Questions.REQUESTS, "REQUESTS"),
        (Questions.USED_CONSULTANTS, "USED_CONSULTANTS"),
        (Questions.FORMAT, "FORMAT"),
        (Questions.REFERRAL, "REFERRAL"),
    ]
    summary_text = build_summary_lines(user_data, fields)
    return  summary_text


def build_feedback_summary(data: dict) -> str:
    """Формує текст повідомлення з відгуком у стилі анкети для менеджерів"""
    fields = [
        (FeedbackQuestions.Q1, "q1"),
        (FeedbackQuestions.Q2, "q2"),
        (FeedbackQuestions.Q3, "q3"),
        (FeedbackQuestions.Q4, "q4"),
    ]

    summary_text = build_summary_lines(data, fields)
    return summary_text


'''
   user_name = user.full_name if user.full_name else "Інформація недоступна"
    user_nickname = f"@{user.username}" if user.username else "Користувач без username"
    name = data.get("NAME", "—")

    header = f"📬 Новий відгук від {user_name} ({user_nickname}):\n\n"
    header += f"Ім'я: {name}\n\n"'''

