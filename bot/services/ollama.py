import logging

from aiogram.enums import ParseMode
from aiogram.types import Message

from bot.dispatcher import bot
from bot.helpers.streaming_response import generate
from config.config_loader import OLLAMA_DEFAULT_MODEL


# Function to send a request to Ollama's API and stream the response to the user
async def ollama_request(message: Message, prompt: str = None):
    if prompt is None:
        prompt = "Why is the sky blue?"  # Default prompt, can be customized

    payload = {
        "model": OLLAMA_DEFAULT_MODEL,  # Model specified from your configuration
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    try:
        full_response = ""
        previous_response = None  # To track previous content
        # Send "typing" action while processing
        await bot.send_chat_action(message.chat.id, "typing")

        # Send an initial message to edit later
        sent_message = await bot.send_message(
            chat_id=message.chat.id,
            text="Processing...",
            parse_mode=ParseMode.MARKDOWN,
        )

        # Process each streamed chunk from the generate function
        async for response_data in generate(payload, prompt):
            msg = response_data.get("message")
            if msg and msg.get("role") == "assistant":
                chunk = msg.get("content", "")  # Get the content chunk
                full_response += chunk

                # Only edit the message if the content has changed
                if full_response != previous_response:
                    await bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=sent_message.message_id,
                        text=full_response,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    previous_response = full_response  # Update the previous response

                # If the response is done, stop processing
                if response_data.get("done"):
                    break

    except Exception as e:
        logging.error(f"-----\n[OllamaAPI-ERR] CAUGHT FAULT!\n{e}\n-----")
        await bot.send_message(
            chat_id=message.chat.id,
            text="Something went wrong while processing your request.",
            parse_mode=ParseMode.MARKDOWN,
        )
