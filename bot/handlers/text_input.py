from aiogram.types import Message

from bot.dispatcher import dp
from bot.services.ollama import ollama_request


@dp.message()
async def handle_text_input(message: Message):
    print(message.chat.type)

    if message.chat.type == "private":
        # Capture the user's input message text as the prompt
        user_prompt = message.text

        # Call the ollama_request function and pass the user's message
        await ollama_request(message=message, prompt=user_prompt)
