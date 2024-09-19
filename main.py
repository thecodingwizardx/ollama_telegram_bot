import asyncio
import logging

from aiogram import Bot, types

import bot.handlers.start  # noqa: F401
import bot.handlers.text_input
from bot.dispatcher import bot, dp  # Import bot and dp


async def set_bot_commands(bot: Bot):
    commands = [
        types.BotCommand(command="start", description="Start"),
        types.BotCommand(
            command="help", description="Shows list of available commands"
        ),
        types.BotCommand(command="history", description="Look through messages"),
    ]
    await bot.set_my_commands(commands)


async def main():
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
