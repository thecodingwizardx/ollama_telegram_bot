import logging

import ollama
from aiogram.enums import ParseMode
from aiogram.types import Message

from bot.dispatcher import bot
from config.config_loader import OLLAMA_DEFAULT_MODEL


# Function to send a request to Ollama's API and stream the response to the user
async def ollama_request(message: Message, prompt: str = None):
    try:
        # Start streaming the response from Ollama API
        stream = ollama.chat(
            model=OLLAMA_DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        # Send an initial message to edit later
        sent_message = await bot.send_message(
            chat_id=message.chat.id,
            text="Processing...",
            parse_mode=ParseMode.MARKDOWN,
        )

        full_response = ""  # To accumulate the streamed content
        previous_response = ""  # To keep track of the last message content

        # Stream chunks and update the same message with the full response
        for chunk in stream:
            chunk_content = chunk["message"]["content"]
            full_response += chunk_content

            # Only edit the message if the content has changed
            if full_response != previous_response:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text=full_response,
                    parse_mode=ParseMode.MARKDOWN,
                )
                previous_response = full_response  # Update the previous response

    except Exception as e:
        logging.error(f"-----\n[OllamaAPI-ERR] CAUGHT FAULT!\n{e}\n-----")
        await bot.send_message(
            chat_id=message.chat.id,
            text="Something went wrong while processing your request.",
            parse_mode=ParseMode.MARKDOWN,
        )
