from aiogram.enums import ParseMode
from aiogram.types import Message

from database.bot_database import BotDatabase

db = BotDatabase()


async def command_start_handler(message: Message):
    """
    This handler receives messages with `/start` command
    """
    user = message.from_user
    chat_id = message.chat.id

    # Store user details in the database
    await db.create_user(
        user_id=user.id,
        chat_id=chat_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    start_message = f"Welcome, <b>{message.from_user.full_name}</b>!"
    await message.answer(
        start_message,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
