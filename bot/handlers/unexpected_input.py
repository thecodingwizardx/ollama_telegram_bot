from aiogram import types
from aiogram.types import Message


async def handle_unexpected_input(message: Message):
    content_type = message.content_type
    user_first_name = message.from_user.first_name

    response = f"I'm sorry {user_first_name}, I can only process text messages. You sent a {content_type}."

    if content_type == types.ContentType.DOCUMENT:
        response += " If you want to share information, please type it as text."
    elif content_type in [types.ContentType.STICKER, types.ContentType.ANIMATION]:
        response += (
            " While I appreciate the sentiment, I can't interpret stickers or GIFs."
        )
    elif content_type == types.ContentType.PHOTO:
        response += " If you want to describe an image, please do so in text."
    elif content_type == types.ContentType.VOICE:
        response += (
            " I don't have voice recognition capabilities. Please type your message."
        )
    elif content_type == types.ContentType.POLL:
        response += " I can't participate in polls. Feel free to ask your question in text form."

    await message.reply(response)
