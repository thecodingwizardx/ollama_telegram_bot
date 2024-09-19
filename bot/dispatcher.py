from aiogram import Bot, Dispatcher

from config.config_loader import TOKEN

bot = Bot(token=TOKEN)  # Initialize the bot
dp = Dispatcher()  # Initialize the dispatcher
