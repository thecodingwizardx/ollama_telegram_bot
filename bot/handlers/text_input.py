# bot/handlers/text_input.py

import yaml
from aiogram.types import Message

from bot.services.ollama import ollama_request
from database.bot_database import BotDatabase

db = BotDatabase()

# Load chat modes from YAML with UTF-8 encoding
with open("config/chat_modes.yml", "r", encoding="utf-8") as file:
    chat_modes = yaml.safe_load(file)


async def handle_text_input(message: Message):
    if message.chat.type == "private":
        # Ensure the user exists in the database
        user = message.from_user
        await db.create_user(
            user_id=user.id,
            chat_id=message.chat.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

        # Get user data
        user_data = await db.get_user(user.id)
        dialog_id = user_data.get("current_dialog_id")

        if not dialog_id:
            # If no current dialog, create one with default 'assistant' mode
            dialog_id = await db.create_dialog(user_id=user.id)
            chat_mode = "assistant"
            mode_info = chat_modes.get(chat_mode, {})
            welcome_message = mode_info.get("welcome_message", "Welcome!")
            parse_mode = mode_info.get("parse_mode", "html")
            await message.answer(welcome_message, parse_mode=parse_mode)
        else:
            # Retrieve the current dialog
            dialog = await db.get_dialog(dialog_id)
            if not dialog:
                # If dialog does not exist, create a new one
                dialog_id = await db.create_dialog(user_id=user.id)
                chat_mode = "assistant"
                mode_info = chat_modes.get(chat_mode, {})
                welcome_message = mode_info.get("welcome_message", "Welcome!")
                parse_mode = mode_info.get("parse_mode", "html")
                await message.answer(welcome_message, parse_mode=parse_mode)
            else:
                chat_mode = dialog.get("chat_mode", "assistant")
                mode_info = chat_modes.get(chat_mode, {})
                parse_mode = mode_info.get("parse_mode", "html")

        # Get the selected mode's information
        mode_info = chat_modes.get(chat_mode, {})
        prompt_start = mode_info.get("prompt_start", "")
        parse_mode = mode_info.get("parse_mode", "html")

        # Combine prompt_start with user input
        combined_prompt = f"{prompt_start}\n\nUser: {message.text}"

        # Call the ollama_request function with the combined prompt
        await ollama_request(
            db,
            dialog_id,
            message=message,
            prompt=combined_prompt,
            parse_mode=parse_mode,
        )
