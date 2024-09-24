import yaml
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Load chat modes from YAML with UTF-8 encoding
with open("config/chat_modes.yml", "r", encoding="utf-8") as file:
    chat_modes = yaml.safe_load(file)


# Helper function to get the mode names
def get_mode_names():
    return [chat_modes[mode]["name"] for mode in chat_modes]


# Handler for the /mode command
async def show_modes(message: types.Message, page: int = 0):
    print("Command Handler: Received /mode command")
    mode_names = get_mode_names()
    per_page = 5  # Number of modes to show per page

    # Create inline keyboard with modes
    keyboard_buttons = []
    start = page * per_page
    end = start + per_page
    for mode_name in mode_names[start:end]:
        keyboard_buttons.append(
            [InlineKeyboardButton(text=mode_name, callback_data=f"mode:{mode_name}")]
        )

    # Add navigation buttons
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(text="⬅️ Back", callback_data=f"page:{page - 1}")
        )
    if end < len(mode_names):
        navigation_buttons.append(
            InlineKeyboardButton(text="➡️ Next", callback_data=f"page:{page + 1}")
        )

    # If we have navigation buttons, add them as a separate row
    if navigation_buttons:
        keyboard_buttons.append(navigation_buttons)

    # Create the markup and assign buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer("Choose a mode:", reply_markup=keyboard)


# Callback handler for pagination
async def process_pagination(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split(":")[1])
    await show_modes(callback_query.message, page=page)


# Callback handler for mode selection
async def process_mode_selection(callback_query: types.CallbackQuery):
    mode_key = callback_query.data.split(":")[1]
    mode_info = chat_modes.get(mode_key, {})
    welcome_message = mode_info.get("welcome_message", "Welcome!")
    parse_mode = mode_info.get("parse_mode", "html")

    await callback_query.message.answer(welcome_message, parse_mode=parse_mode)
