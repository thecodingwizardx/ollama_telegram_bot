from aiogram import types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.dispatcher import dp

start_kb = InlineKeyboardBuilder()

start_kb.row(
    types.InlineKeyboardButton(text="ℹ️ About", callback_data="about"),
    types.InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"),
)


@dp.message(Command("start"))
async def command_start_handler(message: Message):
    """
    This handler receives messages with `/start` command
    """
    start_message = f"Welcome, <b>{message.from_user.full_name}</b>!"
    await message.answer(
        start_message,
        parse_mode=ParseMode.HTML,
        reply_markup=start_kb.as_markup(),
        disable_web_page_preview=True,
    )
