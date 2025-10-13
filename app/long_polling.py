# app/main.py
import asyncio
import signal
import random
import time
import logging
from typing import Any, Callable

from aiohttp import ClientError
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.middlewares.base import BaseMiddleware

from app.config import BOT_TOKEN, GROUP_CHAT_ID, CALENDLY_URL
from app.handlers import ALL_ROUTERS
from app.middleware import ThrottlingMiddleware
from app.logger import logger

from app.handlers.command_classes import BotCommands 
from app.handlers.user_cmnds import COMMANDS

# === Retry з exponential backoff ===
async def retry_request(
    func: Callable,
    retries: int = 5,
    base_delay: float = 1.0,
    *args,
    **kwargs
) -> Any:
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except (ClientError, asyncio.TimeoutError) as e:
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            logger.warning(
                f"⚠️ Помилка мережі ({e}), спроба {attempt+1}/{retries}, чекаю {delay:.2f}s"
            )
            await asyncio.sleep(delay)
    raise Exception("❌ Всі спроби вичерпані")


# === Основна логіка бота ===
async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Ініціалізуємо BotCommands з готовим списком
    bot_commands = BotCommands(COMMANDS)
    bot.set_my_commands(commands=bot_commands.as_telegram_commands())

     # Підключаємо всі роутери
    for router in ALL_ROUTERS:
            self.dp.include_router(router)

    # глобальні дані
    dp["chat_id"] = GROUP_CHAT_ID
    dp["calendly_url"] = CALENDLY_URL

    # middleware
    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.0))

    # підключаємо роутери
    dp.include_router(user_cmnds.router)
    dp.include_router(question_handlers.router)
    dp.include_router(confirmation_handler.router)
    dp.include_router(feedback.router)

   
    # видаляємо старі апдейти
    await retry_request(bot.delete_webhook, drop_pending_updates=True)

    logger.info("🤖 Bot started...")

    try:
        await dp.start_polling(bot, handle_signals=False)
    except Exception:
        logger.exception("❌ Критична помилка під час роботи бота")
    finally:
        await bot.session.close()
        logger.info("🛑 Бот завершив роботу")


# === Запуск з graceful shutdown ===
def run() -> None:
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def _signal_handler(sig: signal.Signals) -> None:
        logger.warning(f"⚠️ Отримано сигнал {sig.name}, завершення роботи...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: _signal_handler(s))

    try:
        loop.create_task(main())
        loop.run_until_complete(stop_event.wait())
    finally:
        loop.close()
        logger.info("✅ Event loop закрито")

