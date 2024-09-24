from aiogram import F
from aiogram.types import Message

from bot.dispatcher import dp
from bot.services.ollama import ollama_request
from database.bot_database import BotDatabase

db = BotDatabase()


@dp.message(F.text)
async def handle_text_input(message: Message):
    print(f"Text Handler: Received message: {message.text}")
    print(f"Entities: {message.entities}")
    print(message.chat.type)

    if message.chat.type == "private":
        # Capture the user's input message text as the prompt
        user = message.from_user
        user_data = await db.get_user(user.id)
        if not user_data.get("current_dialog_id"):
            dialog_id = await db.create_dialog(user_id=user.id)
        else:
            dialog_id = user_data["current_dialog_id"]
        user_prompt = message.text

        # Call the ollama_request function and pass the user's message
        await ollama_request(db, dialog_id, message=message, prompt=user_prompt)
