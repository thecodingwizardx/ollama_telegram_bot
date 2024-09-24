import asyncio
import logging

from aiogram import Bot, F, types
from aiogram.filters import Command

from bot.dispatcher import bot, dp, router
from bot.handlers.bot_settings import command_settings_handler
from bot.handlers.modes import process_mode_selection, process_pagination, show_modes
from bot.handlers.start import command_start_handler
from bot.handlers.text_input import handle_text_input
from bot.handlers.unexpected_input import handle_unexpected_input


# Define bot commands
async def set_bot_commands(bot: Bot):
    commands = [
        types.BotCommand(command="start", description="Start"),
        types.BotCommand(command="help", description="Show available commands"),
        types.BotCommand(command="mode", description="Choose a chatbot mode"),
    ]
    await bot.set_my_commands(commands)


# Main function to start polling
async def main():
    await set_bot_commands(bot)

    # Register command handlers
    router.message.register(command_start_handler, Command("start"))
    router.message.register(show_modes, Command("mode"))
    router.message.register(command_settings_handler, Command("settings"))

    # Callback query handlers
    router.callback_query.register(
        process_pagination, lambda c: c.data.startswith("page:")
    )
    router.callback_query.register(
        process_mode_selection, lambda c: c.data.startswith("mode:")
    )

    # Text input handler (excluding commands)
    router.message.register(
        handle_text_input,
        F.text & (lambda message: not message.is_command()),  # Exclude commands
    )

    # Unexpected input handler (non-text messages)
    router.message.register(handle_unexpected_input, ~F.text)

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
        logging.error("Bot stopped!")
