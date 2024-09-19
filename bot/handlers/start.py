from aiogram.filters import Command
from aiogram.types import Message

from bot.dispatcher import dp


@dp.message(Command("start"))
async def command_start_handler(message: Message):
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        f"Hello {message.from_user.full_name}!, Hi, welcome to ollama!"
    )
