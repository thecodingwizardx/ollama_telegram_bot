# bot/handlers/modes.py

import asyncio  # Import asyncio for handling timeouts

import yaml
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.bot_database import BotDatabase

db = BotDatabase()

# Load chat modes from YAML with UTF-8 encoding
with open("config/chat_modes.yml", "r", encoding="utf-8") as file:
    chat_modes = yaml.safe_load(file)


# Helper function to get list of (key, name) tuples
def get_modes():
    return [(key, value["name"]) for key, value in chat_modes.items()]


# Function to create inline keyboard for a specific page
def create_keyboard(page: int, per_page: int = 5):
    modes = get_modes()
    keyboard_buttons = []
    start = page * per_page
    end = start + per_page
    for key, name in modes[start:end]:
        # Use mode key in callback_data instead of display name
        keyboard_buttons.append(
            [InlineKeyboardButton(text=name, callback_data=f"mode:{key}")]
        )

    # Add navigation buttons if necessary
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Back", callback_data=f"page:{page - 1}")
        )
    if end < len(modes):
        navigation_buttons.append(
            InlineKeyboardButton(text="➡️ Next", callback_data=f"page:{page + 1}")
        )

    # Add navigation buttons as a separate row if they exist
    if navigation_buttons:
        keyboard_buttons.append(navigation_buttons)

    # Create the InlineKeyboardMarkup object
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard


# Dictionary to keep track of timeout tasks per message
# Key: message_id, Value: asyncio.Task
timeout_tasks = {}


async def show_modes(message: types.Message):
    page = 0  # Start at the first page
    keyboard = create_keyboard(page)
    sent_message = await message.answer(
        "Select chat mode (15 modes available):", reply_markup=keyboard
    )

    # Start the timeout handler
    start_timeout(sent_message)


def start_timeout(sent_message: types.Message):
    """Starts or restarts the timeout handler for a given message."""
    message_id = sent_message.message_id

    # If there's an existing timeout task for this message, cancel it
    if message_id in timeout_tasks:
        timeout_tasks[message_id].cancel()

    # Define a coroutine to handle timeout
    async def timeout_handler():
        try:
            await asyncio.sleep(10)  # Wait for 10 seconds
            # Edit the message to inform about timeout and remove the keyboard
            await sent_message.edit_text(
                "Mode selection timed out. Please try again.", reply_markup=None
            )
        except asyncio.CancelledError:
            # The timeout was reset/cancelled
            pass
        except Exception as e:
            # Handle other exceptions (e.g., message already deleted)
            print(f"Timeout handler error: {e}")

    # Start the timeout_handler as a background task
    task = asyncio.create_task(timeout_handler())
    timeout_tasks[message_id] = task


async def process_pagination(callback_query: types.CallbackQuery):
    # Extract the page number from callback data
    page = int(callback_query.data.split(":")[1])
    keyboard = create_keyboard(page)

    # Edit the existing message's text and keyboard
    await callback_query.message.edit_text(
        "Select chat mode (15 modes available):", reply_markup=keyboard
    )

    # Acknowledge the callback to remove the "loading" state
    await callback_query.answer()

    # Restart the timeout handler
    start_timeout(callback_query.message)


async def process_mode_selection(callback_query: types.CallbackQuery):
    # Extract the mode key from callback data
    mode_key = callback_query.data.split(":")[1]
    mode_info = chat_modes.get(mode_key, {})

    if not mode_info:
        await callback_query.answer("Selected mode not found.", show_alert=True)
        return

    # Create a new dialog with the selected mode
    user_id = callback_query.from_user.id
    chat_mode = mode_key
    dialog_id = await db.create_dialog(user_id, chat_mode=chat_mode)

    # Retrieve welcome message and parse mode, with defaults
    welcome_message = mode_info.get("welcome_message", "Welcome!")
    parse_mode = mode_info.get("parse_mode", "html")

    # Send the welcome message
    await callback_query.message.answer(welcome_message, parse_mode=parse_mode)

    # Remove the inline keyboard and inform the user
    try:
        await callback_query.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass  # The message might have been edited already

    # Acknowledge the callback to remove the "loading" state
    await callback_query.answer()

    # Cancel any existing timeout task for this message
    message_id = callback_query.message.message_id
    if message_id in timeout_tasks:
        timeout_tasks[message_id].cancel()
        del timeout_tasks[message_id]
