import yaml
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

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


async def show_modes(message: types.Message):
    page = 0  # Start at the first page
    keyboard = create_keyboard(page)
    await message.answer("Choose a mode:", reply_markup=keyboard)


async def process_pagination(callback_query: types.CallbackQuery):
    # Extract the page number from callback data
    page = int(callback_query.data.split(":")[1])
    keyboard = create_keyboard(page)

    # Edit the existing message's text and keyboard
    await callback_query.message.edit_text("Choose a mode:", reply_markup=keyboard)

    # Acknowledge the callback to remove the "loading" state
    await callback_query.answer()


async def process_mode_selection(callback_query: types.CallbackQuery):
    # Extract the mode key from callback data
    mode_key = callback_query.data.split(":")[1]
    mode_info = chat_modes.get(mode_key, {})

    # Retrieve welcome message and parse mode, with defaults
    welcome_message = mode_info.get("welcome_message", "Welcome!")
    parse_mode = mode_info.get("parse_mode", "html")

    # Send the welcome message
    await callback_query.message.answer(welcome_message, parse_mode=parse_mode)

    # Acknowledge the callback to remove the "loading" state
    await callback_query.answer()
