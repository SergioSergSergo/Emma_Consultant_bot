# app/handlers/__init__.py
from app.handlers import user_cmnds
from app.handlers import confirmation_handler
from app.handlers import feedback
from app.handlers import question_handlers

# Створюємо список роутерів для зручного імпорту
ALL_ROUTERS = [
    user_cmnds.router,
    confirmation_handler.router,
    feedback.router,
    question_handlers.router
]
