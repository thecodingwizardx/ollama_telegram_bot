import asyncio
import logging

import aiogram
import ollama
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.dispatcher import bot, dp
from database.bot_database import BotDatabase

db = BotDatabase()

# Logging setup
logging.basicConfig(level=logging.INFO)

# Timeout duration in seconds
TIMEOUT_DURATION = 15

# Dictionary to keep track of user timeout tasks
user_timeout_tasks = {}


async def delete_message(chat_id: int, message_id: int):
    """
    Deletes a message specified by chat_id and message_id.
    """
    try:
        await bot.delete_message(chat_id, message_id)
        logging.info(f"Deleted message {message_id} in chat {chat_id}")
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            logging.info(f"Message {message_id} not found in chat {chat_id}")
        else:
            logging.error(f"Error deleting message {message_id} in chat {chat_id}: {e}")


async def handle_timeout(message: types.Message, timeout: int, user_id: int):
    """
    Waits for a specified timeout and then deletes the settings message if no interaction occurs.
    """
    try:
        await asyncio.sleep(timeout)
        await delete_message(message.chat.id, message.message_id)
        # await bot.send_message(message.chat.id, "⚙️ Settings menu has timed out.")
        logging.info(f"Timeout executed for user {user_id}")
    except asyncio.CancelledError:
        # Task was canceled because user interacted
        logging.info(f"Timeout task canceled for user {user_id}")
    except Exception as e:
        logging.error(f"Error in handle_timeout for user {user_id}: {e}")
    finally:
        # Remove the task from the dict
        user_timeout_tasks.pop(user_id, None)


async def set_timeout(user_id: int, message: types.Message, timeout: int):
    """
    Sets a timeout for the user by creating a background task.
    Cancels any existing timeout task for the user before setting a new one.
    """
    # Cancel existing task if any
    existing_task = user_timeout_tasks.get(user_id)
    if existing_task:
        existing_task.cancel()
        logging.info(f"Existing timeout task canceled for user {user_id}")

    # Create a new timeout task
    task = asyncio.create_task(handle_timeout(message, timeout, user_id))
    user_timeout_tasks[user_id] = task
    logging.info(f"Timeout task set for user {user_id}")


async def command_settings_handler(message: Message):
    """
    This handler sends a settings menu with inline keyboard buttons and sets a timeout.
    """
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(
        InlineKeyboardButton(text="🧠 AI Model", callback_data="ai_model")
    )
    keyboard_builder.row(
        InlineKeyboardButton(text="🇬🇧 Language (Coming Soon)", callback_data="language")
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text="🙋‍♀️ Your Name (Coming Soon)", callback_data="your_name"
        )
    )
    # Add Exit button
    keyboard_builder.row(
        InlineKeyboardButton(text="🚪 Exit", callback_data="exit_settings")
    )

    keyboard = keyboard_builder.as_markup()
    sent_message = await message.answer("⚙️ Settings:", reply_markup=keyboard)

    # Set a timeout task
    await set_timeout(message.from_user.id, sent_message, TIMEOUT_DURATION)


# Callback handler for AI model button
@dp.callback_query(lambda callback_query: callback_query.data == "ai_model")
async def show_ai_models(callback_query: types.CallbackQuery, set_timeout_flag=True):
    """
    Respond to the AI Model button click by showing the available models and adding back and exit buttons.
    Optionally sets a timeout for the AI model selection menu.
    """
    await (
        callback_query.answer()
    )  # Acknowledge the callback to remove the loading state

    user_id = callback_query.from_user.id
    message = callback_query.message

    # Fetch the available models from Ollama
    try:
        models_response = ollama.list()
        models = models_response["models"]
    except Exception as e:
        logging.error(f"Error fetching models from Ollama: {e}")
        await message.edit_text("Failed to retrieve AI models. Please try again later.")
        return

    # Create a keyboard with AI models, back, and exit buttons
    model_keyboard_builder = InlineKeyboardBuilder()

    # Iterate over the models and add each as a button
    for model in models:
        model_name = model["name"]

        # Check if the user has selected this model
        selected = await db.get_selected_model(user_id) == model_name
        display_text = f"✅ {model_name}" if selected else model_name

        # Add model selection buttons
        model_keyboard_builder.row(
            InlineKeyboardButton(
                text=display_text, callback_data=f"select_model:{model_name}"
            )
        )

    # Add the back and exit buttons
    model_keyboard_builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="back_to_settings"),
        InlineKeyboardButton(text="🚪 Exit", callback_data="exit_settings"),
    )

    # Create the inline keyboard for models and back button
    new_markup = model_keyboard_builder.as_markup()

    # Log current message content and markup for logging
    current_text = message.text
    current_markup = message.reply_markup
    logging.info(f"User {user_id} - Current message text: {current_text}")
    logging.info("New message text: Select a model:")
    logging.info(
        f"Current reply_markup: {current_markup.inline_keyboard if current_markup else None}"
    )
    logging.info(f"New reply_markup: {new_markup.inline_keyboard}")

    try:
        # Compare the current and new inline keyboards
        if (
            current_text == "Select a model:"
            and current_markup
            and current_markup.inline_keyboard == new_markup.inline_keyboard
        ):
            logging.info("Message and keyboard are identical, skipping edit.")
        else:
            await message.edit_text("Select a model:", reply_markup=new_markup)
    except AttributeError:
        # If reply_markup is None, proceed to edit the message
        await message.edit_text("Select a model:", reply_markup=new_markup)
    except aiogram.exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.info("Attempted to edit message without changes.")
        else:
            raise  # Re-raise unexpected exceptions

    # Set a timeout task only if set_timeout_flag is True
    if set_timeout_flag:
        await set_timeout(user_id, message, TIMEOUT_DURATION)


# Callback handler for selecting a model
@dp.callback_query(
    lambda callback_query: callback_query.data.startswith("select_model:")
)
async def select_model(callback_query: types.CallbackQuery):
    selected_model = callback_query.data.split(":", 1)[1]
    user_id = callback_query.from_user.id
    message = callback_query.message

    # Cancel any existing timeout task for the user
    existing_task = user_timeout_tasks.get(user_id)
    if existing_task:
        existing_task.cancel()
        user_timeout_tasks.pop(user_id, None)
        logging.info(
            f"Timeout task canceled for user {user_id} after selecting a model."
        )

    # Get the current selected model
    current_model = await db.get_selected_model(user_id)

    if selected_model == current_model:
        logging.info(
            f"User {user_id} selected the already active model: {selected_model}"
        )
        await callback_query.answer("This model is already selected.", show_alert=False)
        return

    # Store the selected model for the user in the database
    await db.update_user_model(user_id, selected_model)

    # Delete the settings message after selecting the model
    await delete_message(message.chat.id, message.message_id)

    # Send a confirmation message in the chat
    await callback_query.message.answer(
        f"✅ Model changed to **{selected_model}**.", parse_mode="Markdown"
    )

    # Optionally, disable the inline keyboard
    # But since 'show_ai_models' is called with set_timeout_flag=False, no new timeout is set


# Callback handler for Back button
@dp.callback_query(lambda callback_query: callback_query.data == "back_to_settings")
async def back_to_settings(callback_query: types.CallbackQuery):
    """
    Go back to the settings menu when the back button is clicked by editing the existing message.
    Sets a timeout for the settings menu.
    """
    await (
        callback_query.answer()
    )  # Acknowledge the callback to remove the loading state

    user_id = callback_query.from_user.id
    message = callback_query.message

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(
        InlineKeyboardButton(text="🧠 AI Model", callback_data="ai_model")
    )
    keyboard_builder.row(
        InlineKeyboardButton(text="🇬🇧 Language (Coming Soon)", callback_data="language")
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text="🙋‍♀️ Your Name (Coming Soon)", callback_data="your_name"
        )
    )
    # Add Exit button
    keyboard_builder.row(
        InlineKeyboardButton(text="🚪 Exit", callback_data="exit_settings")
    )

    new_markup = keyboard_builder.as_markup()

    # Log current message content and markup for logging
    current_text = message.text
    current_markup = message.reply_markup
    logging.info(f"User {user_id} - Current message text: {current_text}")
    logging.info("New message text: ⚙️ Settings:")
    logging.info(
        f"Current reply_markup: {current_markup.inline_keyboard if current_markup else None}"
    )
    logging.info(f"New reply_markup: {new_markup.inline_keyboard}")

    try:
        # Compare the current and new inline keyboards
        if (
            current_text == "⚙️ Settings:"
            and current_markup
            and current_markup.inline_keyboard == new_markup.inline_keyboard
        ):
            logging.info("Message and keyboard are identical, skipping edit.")
        else:
            await message.edit_text("⚙️ Settings:", reply_markup=new_markup)
    except AttributeError:
        # If reply_markup is None, proceed to edit the message
        await message.edit_text("⚙️ Settings:", reply_markup=new_markup)
    except aiogram.exceptions.TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logging.info("Attempted to edit message without changes.")
        else:
            raise  # Re-raise unexpected exceptions

    # Set a timeout task
    await set_timeout(user_id, message, TIMEOUT_DURATION)


# Callback handler for Exit button
@dp.callback_query(lambda callback_query: callback_query.data == "exit_settings")
async def exit_settings(callback_query: types.CallbackQuery):
    """
    Exits the settings menu by deleting the settings message and canceling any active timeout tasks.
    """
    await (
        callback_query.answer()
    )  # Acknowledge the callback to remove the loading state

    user_id = callback_query.from_user.id
    message = callback_query.message

    # Cancel any existing timeout task for the user
    existing_task = user_timeout_tasks.get(user_id)
    if existing_task:
        existing_task.cancel()
        user_timeout_tasks.pop(user_id, None)
        logging.info(f"Timeout task canceled for user {user_id} upon exit.")

    # Delete the settings message
    await delete_message(message.chat.id, message.message_id)

    # Send a confirmation message
    await message.answer("🚪 Exited the settings menu.")


# Optional: Handle other settings callbacks like "language" and "your_name"
# You can add similar handlers for these callbacks if needed.
# You can add similar handlers for these callbacks if needed.
