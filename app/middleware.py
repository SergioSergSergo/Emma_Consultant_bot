import time
from aiogram.dispatcher.middlewares.base import BaseMiddleware

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self.users = {}

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        now = time.time()

        if user_id in self.users and now - self.users[user_id] < self.rate_limit:
            await event.answer("⏳ Занадто часто. Спробуйте трохи пізніше.")
            return
        self.users[user_id] = now
        return await handler(event, data)