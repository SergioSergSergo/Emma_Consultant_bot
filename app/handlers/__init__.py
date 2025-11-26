# app/handlers/__init__.py
from app.handlers import user_cmnds
from app.handlers import feedback
from app.handlers import fill_brief

# Створюємо список роутерів для зручного імпорту
ALL_ROUTERS = [
    user_cmnds.router,
    feedback.router,
    fill_brief.router,
]
