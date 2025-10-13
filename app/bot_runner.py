# run.py
import os
from aiogram import Dispatcher, Bot

from app.webhook import WebhookServer
from app.handlers import ALL_ROUTERS
from app.logger import logger
from app.config import BOT_TOKEN
from app.middleware import RateLimiter, ThrottlingMiddleware
from app.bot_commands import custom_bot_commands

class BotRunner:
    """
    Єдиний клас для запуску Telegram-бота
    Може працювати як через webhook, так і через polling.
    """
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher()

         # Створюємо спільний RateLimiter
        self.rate_limiter = RateLimiter(limit_per_user=1.0, limit_per_ip=0.2)

        # Підключаємо middleware для POLLING
        self.dp.message.middleware(ThrottlingMiddleware(self.rate_limiter))

        # Підключаємо всі роутери
        for router in ALL_ROUTERS:
            self.dp.include_router(router)

    async def set_bot_commands(self):
        """Встановлення списку команд із зовнішнього класу"""
        try:
            await self.bot.set_my_commands(custom_bot_commands.as_telegram_commands())
            logger.info("✅ Bot commands were successfully set.")
        except Exception as e:
            logger.error(f"⚠️ Failed to set bot commands: {e}")

    async def run_polling(self):
        logger.info("🚀 Starting bot in POLLING mode...")
        try:
            await self.bot.delete_webhook(drop_pending_updates=True)
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.exception("❌ Polling error", exc_info=e)
        finally:
            await self.bot.session.close()
            logger.info("✅ Polling stopped gracefully.")

    async def run_webhook(self):
        """Запуск у режимі webhook"""
        logger.info("🌐 Starting bot in WEBHOOK mode...")
        server = WebhookServer(dispatcher=self.dp)
        await server.run()

    async def run(self):
        """Автоматичний вибір режиму запуску"""
        use_webhook = os.getenv("USE_WEBHOOK", "false").lower() == "true"
        await self.set_bot_commands()
        try:
            if use_webhook:
                await self.run_webhook()
            else:
                await self.run_polling()
        finally:
            # 🧹 Завжди закриваємо бот-сесію
            await self.bot.session.close()
            logger.info("✅ Bot session closed cleanly.")

