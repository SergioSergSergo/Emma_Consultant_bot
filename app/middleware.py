import time
from aiohttp import web
from aiogram import BaseMiddleware
from app.logger import logger

class RateLimiter:
    """
    Універсальний RateLimiter — ядро логіки (спільне для webhook і polling).
    """
    def __init__(self, limit_per_user=1.0, limit_per_ip=0.1):
        self.limit_per_user = limit_per_user  # секунди між запитами користувача (polling)
        self.limit_per_ip = limit_per_ip      # секунди між запитами IP (webhook)
        self._users = {}
        self._ips = {}

    def check_user(self, user_id: int) -> bool:
        """True якщо користувач ще у cooldown."""
        now = time.monotonic()
        last = self._users.get(user_id, 0)
        if now - last < self.limit_per_user:
            return True
        self._users[user_id] = now
        return False

    def check_ip(self, ip: str) -> bool:
        """True якщо IP перевищив ліміт."""
        now = time.monotonic()
        last = self._ips.get(ip, 0)
        if now - last < self.limit_per_ip:
            return True
        self._ips[ip] = now
        return False


# --- Middleware для Aiogram (Polling) ---
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    async def __call__(self, handler, event, data):
        user_id = getattr(event.from_user, "id", None)
        if user_id and self.limiter.check_user(user_id):
            await event.answer("⏳ Занадто часто! Спробуйте трохи пізніше.")
            return
        return await handler(event, data)


class RateLimitMiddleware:
    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    @web.middleware
    async def middleware(self, request, handler):
        try:
            data = await request.json()
            user_id = data.get("message", {}).get("from", {}).get("id")
        except Exception:
            user_id = None

        # Використовуємо user-based throttling для webhook
        if user_id and self.limiter.check_user(user_id):
            logger.warning(f"🚫 Rate limit: user {user_id} — занадто часті запити (ignored)")
            return web.Response(status=200, text="OK (user limited)")

        return await handler(request)
