import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Room, ChatMessage
import base64

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_code}'
        
        # Проверяем авторизацию пользователя
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return
        
        # Проверяем существование комнаты
        room = await self.get_room()
        if not room:
            await self.close()
            return
        
        # Проверяем, находится ли пользователь в комнате
        if not await self.is_user_in_room():
            await self.close()
            return
        
        # Присоединяемся к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Отправляем сообщение о подключении
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': self.scope['user'].username,
                'message': f"{self.scope['user'].username} присоединился к комнате"
            }
        )
    
    async def disconnect(self, close_code):
        # Покидаем группу комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Отправляем сообщение об отключении
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user': self.scope['user'].username,
                'message': f"{self.scope['user'].username} покинул комнату"
            }
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            # Сохраняем сообщение в базу
            await self.save_chat_message(data['message'])
            
            # Отправляем сообщение всем в комнате
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'user': self.scope['user'].username,
                    'message': data['message'],
                    'timestamp': data.get('timestamp', '')
                }
            )
        
        elif message_type == 'drawing':
            # Отправляем действия рисования всем в комнате
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'drawing_data',
                    'user': self.scope['user'].username,
                    'data': data['data'],
                    'action': data.get('action', 'draw')
                }
            )
        
        elif message_type == 'clear_canvas':
            # Отправляем команду очистки холста
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'clear_canvas',
                    'user': self.scope['user'].username
                }
            )
        
        elif message_type == 'save_drawing':
            # Сохраняем рисунок в базу
            await self.save_drawing(data['image_data'])
    
    # Обработчики для разных типов сообщений
    
    async def chat_message(self, event):
        # Отправляем сообщение чата WebSocket клиенту
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'user': event['user'],
            'message': event['message'],
            'timestamp': event.get('timestamp', '')
        }))
    
    async def drawing_data(self, event):
        # Отправляем данные рисования
        await self.send(text_data=json.dumps({
            'type': 'drawing',
            'user': event['user'],
            'data': event['data'],
            'action': event.get('action', 'draw')
        }))
    
    async def clear_canvas(self, event):
        # Отправляем команду очистки
        await self.send(text_data=json.dumps({
            'type': 'clear_canvas',
            'user': event['user']
        }))
    
    async def user_joined(self, event):
        # Уведомление о присоединении пользователя
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': event['message']
        }))
    
    async def user_left(self, event):
        # Уведомление о выходе пользователя
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': event['message']
        }))
    
    # Вспомогательные функции для работы с базой данных
    
    @database_sync_to_async
    def get_room(self):
        try:
            return Room.objects.get(code=self.room_code, is_active=True)
        except Room.DoesNotExist:
            return None
    
    @database_sync_to_async
    def is_user_in_room(self):
        try:
            room = Room.objects.get(code=self.room_code)
            user = self.scope['user']
            return room.is_user_in_room(user)
        except Room.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_chat_message(self, message):
        room = Room.objects.get(code=self.room_code)
        ChatMessage.objects.create(
            room=room,
            user=self.scope['user'],
            message=message
        )
    
    @database_sync_to_async
    def save_drawing(self, image_data):
        room = Room.objects.get(code=self.room_code)
        Drawing.objects.create(
            room=room,
            image_data=image_data,
            created_by=self.scope['user']
        )