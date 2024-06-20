
import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class RedirectConsumer(WebsocketConsumer):
    def connect(self):
        user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'user_{user_id}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def check_redirect(self, event):
        from .models import Order
        user_id = event['event']['user_id']
        profile = Order.objects.filter(user=user_id).order_by('-created_at').first()
        if profile.completed:
            self.send(text_data=json.dumps({
                'redirect_url': event['event']['redirect_url']
            }))

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'orders'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'order.message',
                'order': data['order']
            }
        )

    async def order_message(self, event):
        order = event['order']

        await self.send(text_data=json.dumps({
            'order': order
        }))