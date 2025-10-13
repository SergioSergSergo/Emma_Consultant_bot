from typing import List
from aiogram.types import BotCommand
from typing import List

class BotCommandItem:
    """Представляє одну команду бота"""

    def __init__(
        self,
        key: str,
        command: str,
        short_desc: str,
        long_desc: str,
        access: str = "always",
        admin_level: int | None = None  # None = звичайний користувач, 0..n = рівень доступу
    ):
        self.key = key                  # Унікальний ключ команди
        self.command = command          # Текст команди (наприклад, /start)
        self.short_desc = short_desc    # Короткий опис
        self.long_desc = long_desc      # Детальний опис
        self.access = access            # Доступ: "always" або "after_booking"
        self.admin_level = admin_level  # None = звичайний, 0..n = рівень доступу адміністратора

    def __repr__(self):
        return (
            f"<BotCommandItem {self.command} ({self.key}, access={self.access}, admin_level={self.admin_level})>"
        )

class BotCommands:
    """Collection of all bot commands"""
    
    def __init__(self, commands: List[BotCommandItem]):
        self._commands = commands  # store the list passed in

    def all(self, after_booking: bool = False) -> List[BotCommandItem]:
        if after_booking:
            return self._commands
        else:
            return [cmd for cmd in self._commands if cmd.access == "always"]

    def get_command_by_key(self, key: str) -> BotCommandItem | None:
        for cmd in self._commands:
            if cmd.key == key:
                return cmd
        return None

    def as_telegram_commands(self, after_booking: bool = False) -> List[BotCommand]:
        return [
            BotCommand(command=cmd.command.lstrip("/"), description=cmd.short_desc)
            for cmd in self.all(after_booking=after_booking)
        ]



COMMANDS = [
    BotCommandItem(
        key="start",
        command="/start",
        short_desc="Почати бот",
        long_desc="Почати бот та побачити привітальне повідомлення",
        access="always"
    ),
    BotCommandItem(
        key="help",
        command="/help",
        short_desc="Довідка",
        long_desc="Показує довідкове повідомлення",
        access="always"
    ),
    BotCommandItem(
        key="restart",
        command="/restart_questionnaire",
        short_desc="розпочати опитування спочатку",
        long_desc="Обнуляє дані і повертає до першого питання анкети",
        access="always"
    ),
]

custom_bot_commands = BotCommands(COMMANDS)
