# database/bot_database.py

import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from config.config_loader import MONGO_URI, OLLAMA_DEFAULT_MODEL


class BotDatabase:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[
            "ollama_telegram_bot_db"
        ]  # Define your database name here
        self.users_collection = self.db["users"]
        self.dialogs_collection = self.db["dialogs"]

    async def create_user(self, user_id, chat_id, username, first_name, last_name):
        user_data = {
            "_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_interaction": datetime.now(),
            "first_seen": datetime.now(),
            "current_dialog_id": None,
            # Removed 'selected_mode' field
        }
        existing_user = await self.users_collection.find_one({"_id": user_id})
        if existing_user:
            # If the user exists, update the `last_interaction`
            await self.users_collection.update_one(
                {"_id": user_id}, {"$set": {"last_interaction": datetime.now()}}
            )
        else:
            # If the user does not exist, insert the new user document
            await self.users_collection.insert_one(user_data)

    async def create_dialog(self, user_id, chat_mode="assistant", model="test"):
        dialog_id = str(uuid.uuid4())  # Use UUID for unique dialog_id
        dialog_data = {
            "_id": dialog_id,
            "user_id": user_id,
            "chat_mode": chat_mode,  # Set chat_mode
            "start_time": datetime.now(),
            "model": model,
            "messages": [],
        }
        # Insert the dialog into the dialogs collection
        await self.dialogs_collection.insert_one(dialog_data)

        # Update the current dialog ID in the user's document
        await self.users_collection.update_one(
            {"_id": user_id}, {"$set": {"current_dialog_id": dialog_id}}
        )
        return dialog_id

    async def add_message_to_dialog(
        self, user_id, dialog_id, user_message, bot_message
    ):
        message_data = {
            "user": user_message,  # User's message
            "bot": bot_message,  # Bot's message
            "date": datetime.now(),  # Current timestamp
        }

        # Append the message to the dialog's messages array
        await self.dialogs_collection.update_one(
            {"_id": dialog_id, "user_id": user_id},
            {"$push": {"messages": message_data}},  # Use $push to append to the array
        )

    async def get_user(self, user_id):
        # Fetch user from the database
        return await self.users_collection.find_one({"_id": user_id})

    async def get_dialog(self, dialog_id):
        # Fetch dialog from the database
        return await self.dialogs_collection.find_one({"_id": dialog_id})

    async def update_user_last_interaction(self, user_id):
        # Update the user's last_interaction timestamp
        await self.users_collection.update_one(
            {"_id": user_id}, {"$set": {"last_interaction": datetime.now()}}
        )

    async def update_user_model(self, user_id, selected_model):
        await self.users_collection.update_one(
            {"_id": user_id}, {"$set": {"selected_model": selected_model}}
        )

    async def get_selected_model(self, user_id):
        user = await self.users_collection.find_one({"_id": user_id})
        return user.get("selected_model", OLLAMA_DEFAULT_MODEL)
