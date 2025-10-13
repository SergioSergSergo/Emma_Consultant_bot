import asyncio
import ssl
import json
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from app.config import BOT_TOKEN, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT
from app.logger import logger
from app.middleware import RateLimiter, RateLimitMiddleware


class WebhookServer:
    """
    🌐 Надійний aiohttp-сервер для Telegram Webhook.
    Використовується з aiogram 3.x
    """

    def __init__(self, dispatcher: Dispatcher):
        self.dp = dispatcher
        self.bot = Bot(token=BOT_TOKEN)
        self.app = web.Application(client_max_size=10*1024**2)  # 10 MB max
        self.runner = None
        self.site = None

        # Використовуємо той самий RateLimiter
        limiter = RateLimiter(limit_per_user=1.0, limit_per_ip=0.2)
        self.app.middlewares.append(RateLimitMiddleware(limiter).middleware)    

        # Додаємо endpoint для отримання оновлень
        self.app.router.add_post("/webhook", self.handle_update)
        # Healthcheck endpoint (для перевірки стану сервера)
        self.app.router.add_get("/health", self.health_check)
        self.app.router.add_get("/", self.handle_root)
        self.app.router.add_get("/favicon.ico", self.handle_favicon)


    async def handle_favicon(self, request):
        return web.Response(status=204)

    async def handle_root(self, request):
        return web.Response(text="Bot is running!")
      
    async def handle_update(self, request: web.Request) -> web.Response:
        """
        Основний обробник оновлень від Telegram.
        Приймає JSON, перетворює на Update, відправляє у Dispatcher.
        """
        try:
            data = await request.json()
            update = Update(**data)
            await self.dp.feed_update(self.bot, update)
            return web.Response(status=200)
        except json.JSONDecodeError:
            logger.warning("⚠️ Received non-JSON update.")
            return web.Response(status=400, text="Invalid JSON")
        except Exception as e:
            logger.exception(f"❌ Error handling update: {e}")
            return web.Response(status=500, text="Internal Server Error")

    async def health_check(self, request: web.Request) -> web.Response:
        """Простий healthcheck (можна використати для моніторингу у Docker/K8s)."""
        return web.json_response({"status": "ok", "mode": "webhook"})


    async def set_webhook(self):
        """
        Встановлює webhook у Telegram API.
        Якщо він уже встановлений, перевіряє коректність URL.
        """
        webhook_info = await self.bot.get_webhook_info()

        if webhook_info.url != WEBHOOK_URL:
            await self.bot.set_webhook(
                url=WEBHOOK_URL,
                drop_pending_updates=True,
                allowed_updates=self.dp.resolve_used_update_types(),
            )
            logger.info(f"🔗 Webhook set to: {WEBHOOK_URL}")
        else:
            logger.info(f"✅ Webhook already set: {WEBHOOK_URL}")

    async def delete_webhook(self):
        """Видаляє webhook (наприклад, при зупинці)."""
        try:
            await self.bot.delete_webhook(drop_pending_updates=False)
            logger.info("🧹 Webhook deleted successfully.")
        except Exception as e:
            logger.error(f"⚠️ Failed to delete webhook: {e}")

    async def run(self, ssl_cert_path: str = None, ssl_key_path: str = None):
        """
        Запускає aiohttp вебсервер.
        Якщо вказані шляхи до SSL-сертифікатів — запускає HTTPS.
        """
        logger.info("🌐 Starting webhook server...")

        # 1️⃣ Встановлюємо webhook у Telegram
        await self.set_webhook()

        # 2️⃣ Готуємо вебсервер
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        ssl_context = None
        if ssl_cert_path and ssl_key_path:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(ssl_cert_path, ssl_key_path)
            logger.info("🔒 SSL enabled for webhook server.")

        # 3️⃣ Створюємо сайт (HTTP або HTTPS)
        self.site = web.TCPSite(
            self.runner,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
            ssl_context=ssl_context,
        )

        await self.site.start()
        logger.info(f"🚀 Webhook server started on {WEBAPP_HOST}:{WEBAPP_PORT}")

        # 4️⃣ Безкінечний цикл (щоб тримати сервер активним)
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            logger.info("🛑 Webhook server received shutdown signal.")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Коректне завершення сервера."""
        logger.info("🔻 Shutting down webhook server...")
        try:
            await self.delete_webhook()
            if self.runner:
                await self.runner.cleanup()
            await self.bot.session.close()
            logger.info("✅ Webhook server stopped cleanly.")
        except Exception as e:
            logger.exception(f"❌ Error during shutdown: {e}")
