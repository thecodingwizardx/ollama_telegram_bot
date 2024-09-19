import ollama
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.dispatcher import dp

# Global variable to store the selected model for each user
user_selected_model = {}


# Handler for the /settings command
@dp.message(Command("settings"))
async def command_settings_handler(message: Message):
    """
    This handler sends a settings menu with inline keyboard buttons.
    """

    # Create the inline keyboard buttons with emojis
    keyboard_builder = InlineKeyboardBuilder()

    # Add buttons in a row-wise layout
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

    # Create the inline keyboard
    keyboard = keyboard_builder.as_markup()

    # Send the message with the keyboard
    await message.answer("⚙️ Settings:", reply_markup=keyboard)


# Callback handler for AI model button
@dp.callback_query(lambda callback_query: callback_query.data == "ai_model")
async def show_ai_models(callback_query):
    """
    Respond to the AI Model button click by showing the available models and adding a back button.
    """

    # Fetch the available models from Ollama
    models_response = ollama.list()
    models = models_response["models"]

    # Create a keyboard with AI models and a back button
    model_keyboard_builder = InlineKeyboardBuilder()

    # Iterate over the models and add each as a button
    for model in models:
        model_name = model["name"]

        # Check if the user has selected this model
        selected = user_selected_model.get(callback_query.from_user.id) == model_name
        display_text = f"✅ {model_name}" if selected else model_name

        # Add model selection buttons
        model_keyboard_builder.row(
            InlineKeyboardButton(
                text=display_text, callback_data=f"select_model:{model_name}"
            )
        )

    # Add the back button with an arrow icon
    model_keyboard_builder.row(
        InlineKeyboardButton(text="🔙 Back", callback_data="back_to_settings")
    )

    # Create the inline keyboard for models and back button
    model_keyboard = model_keyboard_builder.as_markup()

    # Avoid editing if the text and keyboard are the same as before
    if (
        callback_query.message.text != "Select a model:"
        or callback_query.message.reply_markup != model_keyboard
    ):
        await callback_query.message.edit_text(
            "Select a model:", reply_markup=model_keyboard
        )


# Callback handler for selecting a model
@dp.callback_query(
    lambda callback_query: callback_query.data.startswith("select_model:")
)
async def select_model(callback_query):
    """
    Handle model selection and mark the selected model with a green tick (✅).
    """
    # Extract the selected model from callback data
    selected_model = callback_query.data.split(":")[1]

    # Store the selected model for the user
    user_selected_model[callback_query.from_user.id] = selected_model

    # Refresh the model list with the selected model marked with a green tick
    await show_ai_models(callback_query)


# Callback handler for Back button
@dp.callback_query(lambda callback_query: callback_query.data == "back_to_settings")
async def back_to_settings(callback_query):
    """
    Go back to the settings menu when the back button is clicked by editing the existing message.
    """
    # Create the inline keyboard buttons with emojis
    keyboard_builder = InlineKeyboardBuilder()

    # Add buttons in a row-wise layout
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

    # Create the inline keyboard
    keyboard = keyboard_builder.as_markup()

    # Avoid editing if the text and keyboard are the same as before
    if (
        callback_query.message.text != "⚙️ Settings:"
        or callback_query.message.reply_markup != keyboard
    ):
        await callback_query.message.edit_text("⚙️ Settings:", reply_markup=keyboard)
