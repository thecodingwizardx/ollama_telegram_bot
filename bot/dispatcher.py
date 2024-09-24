from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

from config.config_loader import TOKEN

bot = Bot(token=TOKEN)  # Initialize the bot
dp = Dispatcher(storage=MemoryStorage())
# Create the router
router = Router()

# Connect the router to the dispatcher
dp.include_router(router)
