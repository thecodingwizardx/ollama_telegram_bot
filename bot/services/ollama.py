# bot/services/ollama.py

import asyncio
import logging
import time

from aiogram.enums.parse_mode import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import Message

from bot.dispatcher import bot
from config.config_loader import OLLAMA_DEFAULT_MODEL, client


# Function to send a request to Ollama's API and stream the response to the user
async def ollama_request(
    db, parse_mode, dialog_id, message: Message, prompt: str = None
):
    try:
        # Start streaming the response from Ollama API
        stream = await client.chat(
            model=OLLAMA_DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        # Send an initial message to edit later
        sent_message = await bot.send_message(
            chat_id=message.chat.id,
            text="Processing...",
            parse_mode=ParseMode.HTML,  # Ensure parse_mode is uppercase as required by Aiogram
        )

        full_response = ""  # To accumulate the streamed content
        last_edit_time = 0  # Timestamp of the last edit
        min_edit_interval = 1  # Minimum interval between edits in seconds
        buffer_threshold = 50  # Minimum number of new characters before editing

        buffer_count = 0  # Number of new characters since last edit

        async for chunk in stream:
            chunk_content = chunk["message"]["content"]
            full_response += chunk_content
            buffer_count += len(chunk_content)

            current_time = time.time()
            time_since_last_edit = current_time - last_edit_time

            if (
                buffer_count >= buffer_threshold
                and time_since_last_edit >= min_edit_interval
            ):
                try:
                    await bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=sent_message.message_id,
                        text=full_response,
                        parse_mode=ParseMode.HTML,
                    )
                    last_edit_time = current_time
                    buffer_count = 0  # Reset buffer count after successful edit
                except TelegramRetryAfter as e:
                    wait_time = e.retry_after
                    logging.warning(
                        f"Rate limited on EditMessageText. Waiting for {wait_time} seconds."
                    )
                    await asyncio.sleep(wait_time)
                except TelegramBadRequest as e:
                    if "message is not modified" in str(e):
                        pass  # Ignore if message hasn't changed
                    else:
                        logging.error(f"TelegramBadRequest Error: {e}")
                        raise e

        # After streaming completes, ensure the final response is updated
        if buffer_count > 0:
            try:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text=full_response,
                    parse_mode=parse_mode,
                )
            except TelegramRetryAfter as e:
                wait_time = e.retry_after
                logging.warning(
                    f"Rate limited on final EditMessageText. Waiting for {wait_time} seconds."
                )
                await asyncio.sleep(wait_time)
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=sent_message.message_id,
                    text=full_response,
                    parse_mode=parse_mode,
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    pass
                else:
                    logging.error(f"TelegramBadRequest Error on final edit: {e}")
                    raise e

        # Store bot's response in the dialog
        await db.add_message_to_dialog(
            user_id=message.from_user.id,
            dialog_id=dialog_id,
            user_message=prompt,
            bot_message=full_response,
        )

    except TelegramRetryAfter as e:
        wait_time = e.retry_after
        logging.warning(
            f"Rate limited on SendMessage. Waiting for {wait_time} seconds."
        )
        await asyncio.sleep(wait_time)
        # Retry sending the error message
        try:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Something went wrong while processing your request.",
                parse_mode=parse_mode,
            )
        except Exception as inner_e:
            logging.error(f"Failed to send error message after rate limit: {inner_e}")

    except Exception as e:
        logging.error(f"-----\n[OllamaAPI-ERR] CAUGHT FAULT!\n{e}\n-----")
        try:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Something went wrong while processing your request.",
                parse_mode=parse_mode,
            )
        except TelegramRetryAfter as e:
            wait_time = e.retry_after
            logging.warning(
                f"Rate limited on SendMessage during exception handling. Waiting for {wait_time} seconds."
            )
            await asyncio.sleep(wait_time)
            await bot.send_message(
                chat_id=message.chat.id,
                text="Something went wrong while processing your request.",
                parse_mode=parse_mode,
            )
        except TelegramBadRequest as e:
            logging.error(f"TelegramBadRequest Error while sending error message: {e}")
