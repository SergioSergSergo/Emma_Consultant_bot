import asyncio
from app.bot_runner import BotRunner
from app.logger import logger

if __name__ == "__main__":
    try:
        asyncio.run(BotRunner().run())
    except KeyboardInterrupt:
        logger.info("🛑 Graceful shutdown.")
