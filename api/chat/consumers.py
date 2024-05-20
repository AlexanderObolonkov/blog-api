import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated or user.is_anonymous:
            await self.close()
        await self.accept()
        await self.channel_layer.group_add("chat_group", self.channel_name)
        messages = await self.get_messages_async()
        async for message in messages:
            text_data = await self.get_text_data(message)
            await self.send(text_data=json.dumps(text_data))
        print("connected")

    async def disconnect(self, close_code):
        print("disconnecting")

    async def receive(self, text_data):
        user = self.scope["user"]
        if not user.is_authenticated or user.is_anonymous:
            await self.close()
        data = json.loads(text_data)
        message = data["message"]
        new_message = await self.save_message_async(user, message)
        local_timestamp = timezone.localtime(new_message.timestamp)
        await self.channel_layer.group_send(
            "chat_group",
            {
                "type": "chat.message",
                "message": new_message.content,
                "user": user.username,
                "timestamp": local_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
        print("message sent")

    async def get_text_data(self, message: Message):
        user = await sync_to_async(lambda: message.user.username)()
        local_timestamp = timezone.localtime(message.timestamp)
        text_data = {
            "message": message.content,
            "user": user,
            "timestamp": local_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return text_data

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_messages_async(self):
        return Message.objects.all()

    @database_sync_to_async
    def save_message_async(self, user, message):
        return Message.objects.create(user=user, content=message)
