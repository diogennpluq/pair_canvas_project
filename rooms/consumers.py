import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Room, ChatMessage, Drawing


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

        # Для режима "По очереди" отправляем состояние игры
        room = await self.get_room()
        if room and room.mode == 'turn':
            await self.send_game_state(room)
    
    async def disconnect(self, close_code):
        # Покидаем группу комнаты
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception:
            pass
        
        # Не отправляем сообщение об отключении, чтобы избежать ошибок при закрытии
        # if hasattr(self, 'scope') and self.scope.get('user'):
        #     await self.channel_layer.group_send(
        #         self.room_group_name,
        #         {
        #             'type': 'user_left',
        #             'user': self.scope['user'].username,
        #             'message': f"{self.scope['user'].username} покинул комнату"
        #         }
        #     )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if not message_type:
                return

            if message_type == 'chat_message':
                # Проверяем наличие сообщения
                message = data.get('message', '')
                if not message:
                    return
                    
                # Сохраняем сообщение в базу
                await self.save_chat_message(message)

                # Отправляем сообщение всем в комнате
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'user': self.scope['user'].username,
                        'message': message,
                        'timestamp': data.get('timestamp', '')
                    }
                )

            elif message_type == 'drawing':
                # Проверяем наличие данных
                if 'data' not in data:
                    return

                # Отправляем действия рисования всем в комнате (включая sequence ID)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'drawing_data',
                        'user': self.scope['user'].username,
                        'data': data['data'],
                        'action': data.get('action', 'draw'),
                        'seq': data.get('seq', 0)
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
                # Проверяем наличие данных изображения
                image_data = data.get('image_data', '')
                if not image_data:
                    return

                # Сохраняем рисунок в базу
                await self.save_drawing(image_data)
                
            elif message_type == 'tool_change':
                # Отправляем информацию об изменении инструмента
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'tool_change',
                        'user': self.scope['user'].username,
                        'tool': data.get('tool', 'brush'),
                        'color': data.get('color', '#000000'),
                        'size': data.get('size', 10)
                    }
                )
                
            elif message_type == 'drawing_start':
                # Отправляем событие начала рисования
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'drawing_start',
                        'user': self.scope['user'].username,
                        'tool': data.get('tool', 'brush'),
                        'color': data.get('color', '#000000'),
                        'size': data.get('size', 10)
                    }
                )
                
            elif message_type == 'drawing_end':
                # Отправляем событие окончания рисования
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'drawing_end',
                        'user': self.scope['user'].username,
                        'tool': data.get('tool', 'brush')
                    }
                )
                
            elif message_type == 'ping':
                # Ответ на ping для поддержания соединения
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))

        except json.JSONDecodeError:
            # Некорректный JSON, закрываем соединение
            await self.close()
        except Exception as e:
            # Логгируем ошибку и закрываем соединение
            print(f"WebSocket error: {e}")
            await self.close()
    
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
        # Отправляем данные рисования (включая sequence ID)
        await self.send(text_data=json.dumps({
            'type': 'drawing',
            'user': event['user'],
            'data': event['data'],
            'action': event.get('action', 'draw'),
            'seq': event.get('seq', 0)
        }))

    async def clear_canvas(self, event):
        # Отправляем команду очистки
        await self.send(text_data=json.dumps({
            'type': 'clear_canvas',
            'user': event['user']
        }))

    async def tool_change(self, event):
        # Отправляем информацию об изменении инструмента
        await self.send(text_data=json.dumps({
            'type': 'tool_change',
            'user': event['user'],
            'tool': event.get('tool', 'brush'),
            'color': event.get('color', '#000000'),
            'size': event.get('size', 10)
        }))

    async def drawing_start(self, event):
        # Отправляем событие начала рисования
        await self.send(text_data=json.dumps({
            'type': 'drawing_start',
            'user': event['user'],
            'tool': event.get('tool', 'brush'),
            'color': event.get('color', '#000000'),
            'size': event.get('size', 10)
        }))

    async def drawing_end(self, event):
        # Отправляем событие окончания рисования
        await self.send(text_data=json.dumps({
            'type': 'drawing_end',
            'user': event['user'],
            'tool': event.get('tool', 'brush')
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

    async def game_state_update(self, event):
        # Отправка обновления состояния игры
        await self.send(text_data=json.dumps({
            'type': 'game_state_update',
            **event['data']
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
    
    async def send_game_state(self, room):
        """Отправка состояния игры клиенту"""
        user = self.scope['user']
        is_current_drawer = False

        if room.mode == 'turn':
            current_turn = await self.get_current_turn(room)
            is_current_drawer = current_turn == user

        data = {
            'turn_count': room.turn_count,
            'max_turns': room.max_turns,
            'is_current_drawer': is_current_drawer,
        }

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_state_update',
                'data': data
            }
        )

    @database_sync_to_async
    def get_current_turn(self, room):
        """Получение текущего хода (async-safe)"""
        return room.current_turn