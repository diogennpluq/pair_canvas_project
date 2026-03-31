from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Room, ChatMessage, Drawing
import json

CustomUser = get_user_model()


class RoomModelTest(TestCase):
    """Тесты для модели Room"""

    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username='creator',
            email='creator@test.com',
            password='pass123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='participant',
            email='participant@test.com',
            password='pass123'
        )

    def test_create_room_auto_code(self):
        """Создание комнаты автоматически генерирует код"""
        room = Room.objects.create(creator=self.user1)
        self.assertIsNotNone(room.code)
        self.assertEqual(len(room.code), 6)
        self.assertTrue(room.code.isalnum())

    def test_create_room_custom_code(self):
        """Создание комнаты с заданным кодом"""
        room = Room.objects.create(creator=self.user1, code='TEST123')
        self.assertEqual(room.code, 'TEST123')

    def test_room_unique_code(self):
        """Код комнаты должен быть уникальным"""
        Room.objects.create(creator=self.user1, code='UNIQUE')
        with self.assertRaises(Exception):
            Room.objects.create(creator=self.user2, code='UNIQUE')

    def test_has_space_true(self):
        """has_space возвращает True если нет участника"""
        room = Room.objects.create(creator=self.user1)
        self.assertTrue(room.has_space())

    def test_has_space_false(self):
        """has_space возвращает False если есть участник"""
        room = Room.objects.create(creator=self.user1, participant=self.user2)
        self.assertFalse(room.has_space())

    def test_has_space_false_inactive(self):
        """has_space возвращает False если комната неактивна"""
        room = Room.objects.create(creator=self.user1, is_active=False)
        self.assertFalse(room.has_space())

    def test_get_users_with_participant(self):
        """get_users возвращает обоих пользователей"""
        room = Room.objects.create(creator=self.user1, participant=self.user2)
        users = room.get_users()
        self.assertEqual(len(users), 2)
        self.assertIn(self.user1, users)
        self.assertIn(self.user2, users)

    def test_get_users_without_participant(self):
        """get_users возвращает только создателя"""
        room = Room.objects.create(creator=self.user1)
        users = room.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.user1)

    def test_is_user_in_room_creator(self):
        """is_user_in_room возвращает True для создателя"""
        room = Room.objects.create(creator=self.user1)
        self.assertTrue(room.is_user_in_room(self.user1))

    def test_is_user_in_room_participant(self):
        """is_user_in_room возвращает True для участника"""
        room = Room.objects.create(creator=self.user1, participant=self.user2)
        self.assertTrue(room.is_user_in_room(self.user2))

    def test_is_user_in_room_stranger(self):
        """is_user_in_room возвращает False для постороннего"""
        room = Room.objects.create(creator=self.user1)
        stranger = CustomUser.objects.create_user(
            username='stranger',
            email='stranger@test.com',
            password='pass'
        )
        self.assertFalse(room.is_user_in_room(stranger))

    def test_room_str_representation(self):
        """Строковое представление комнаты"""
        room = Room.objects.create(creator=self.user1, code='ABC123', mode='free')
        self.assertIn('ABC123', str(room))
        self.assertIn('Свободное рисование', str(room))

    def test_room_mode_choices(self):
        """Проверка режимов комнаты"""
        room_free = Room.objects.create(creator=self.user1, code='FREE01', mode='free')
        room_turn = Room.objects.create(creator=self.user1, code='TURN01', mode='turn')
        room_mirror = Room.objects.create(creator=self.user1, code='MIRR01', mode='mirror')

        self.assertEqual(room_free.get_mode_display(), 'Свободное рисование')
        self.assertEqual(room_turn.get_mode_display(), 'По очереди')
        self.assertEqual(room_mirror.get_mode_display(), 'Зеркало')


class ChatMessageModelTest(TestCase):
    """Тесты для модели ChatMessage"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='chatuser',
            email='chatuser@test.com',
            password='pass123'
        )
        self.room = Room.objects.create(creator=self.user, code='CHAT01')

    def test_create_chat_message(self):
        """Создание сообщения чата"""
        message = ChatMessage.objects.create(
            room=self.room,
            user=self.user,
            message='Hello, World!'
        )
        self.assertEqual(message.message, 'Hello, World!')
        self.assertIsNotNone(message.timestamp)

    def test_chat_message_str(self):
        """Строковое представление сообщения"""
        message = ChatMessage.objects.create(
            room=self.room,
            user=self.user,
            message='Test message'
        )
        self.assertIn('chatuser', str(message))
        self.assertIn('Test message', str(message))

    def test_chat_message_ordering(self):
        """Сообщения сортируются по времени"""
        msg1 = ChatMessage.objects.create(room=self.room, user=self.user, message='First')
        msg2 = ChatMessage.objects.create(room=self.room, user=self.user, message='Second')
        messages = list(ChatMessage.objects.all())
        self.assertEqual(messages[0].message, 'First')
        self.assertEqual(messages[1].message, 'Second')


class DrawingModelTest(TestCase):
    """Тесты для модели Drawing"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='artist',
            email='artist@test.com',
            password='pass123'
        )
        self.room = Room.objects.create(creator=self.user, code='DRAW01')

    def test_create_drawing(self):
        """Создание рисунка"""
        drawing = Drawing.objects.create(
            room=self.room,
            image_data='base64_encoded_image_data',
            created_by=self.user
        )
        self.assertEqual(drawing.image_data, 'base64_encoded_image_data')
        self.assertEqual(drawing.created_by, self.user)

    def test_drawing_str(self):
        """Строковое представление рисунка"""
        drawing = Drawing.objects.create(
            room=self.room,
            image_data='test_data',
            created_by=self.user
        )
        self.assertIn('DRAW01', str(drawing))

    def test_drawing_ordering(self):
        """Рисунки сортируются по убыванию времени"""
        drawing1 = Drawing.objects.create(room=self.room, image_data='data1', created_by=self.user)
        drawing2 = Drawing.objects.create(room=self.room, image_data='data2', created_by=self.user)
        drawings = list(Drawing.objects.all())
        self.assertEqual(drawings[0].image_data, 'data2')  # Новый первый
        self.assertEqual(drawings[1].image_data, 'data1')


class RoomViewsTest(TestCase):
    """Тесты для views комнат"""

    def setUp(self):
        self.client = Client()
        self.user1 = CustomUser.objects.create_user(
            username='roomcreator',
            email='roomcreator@test.com',
            password='pass123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='roomparticipant',
            email='roomparticipant@test.com',
            password='pass123'
        )

    def test_home_view(self):
        """Главная страница доступна всем"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rooms/home.html')

    def test_create_room_requires_login(self):
        """Создание комнаты требует авторизации"""
        response = self.client.get(reverse('create_room'))
        self.assertEqual(response.status_code, 302)

    def test_create_room_post(self):
        """Создание комнаты через POST"""
        self.client.login(username='roomcreator', password='pass123')
        response = self.client.post(reverse('create_room'), {'mode': 'free'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(creator=self.user1).exists())

    def test_join_room_requires_login(self):
        """Присоединение к комнате требует авторизации"""
        response = self.client.get(reverse('join_room'))
        self.assertEqual(response.status_code, 302)

    def test_join_room_success(self):
        """Успешное присоединение к комнате"""
        self.client.login(username='roomcreator', password='pass123')
        room = Room.objects.create(creator=self.user1, code='JOIN01')

        self.client.logout()
        self.client.login(username='roomparticipant', password='pass123')
        response = self.client.post(reverse('join_room'), {'room_code': 'JOIN01'})

        self.assertEqual(response.status_code, 302)
        room.refresh_from_db()
        self.assertEqual(room.participant, self.user2)

    def test_join_room_not_found(self):
        """Присоединение к несуществующей комнате"""
        self.client.login(username='roomparticipant', password='pass123')
        response = self.client.post(reverse('join_room'), {'room_code': 'INVALID'})
        self.assertEqual(response.status_code, 200)

    def test_room_detail_requires_login(self):
        """Детальная страница комнаты требует авторизации"""
        room = Room.objects.create(creator=self.user1, code='DETAIL01')
        response = self.client.get(reverse('room_detail', args=['DETAIL01']))
        self.assertEqual(response.status_code, 302)

    def test_room_detail_access(self):
        """Доступ к комнате имеют только участники"""
        self.client.login(username='roomcreator', password='pass123')
        room = Room.objects.create(creator=self.user1, code='ACCESS01')

        response = self.client.get(reverse('room_detail', args=['ACCESS01']))
        self.assertEqual(response.status_code, 200)

    def test_room_detail_no_access(self):
        """Нет доступа к чужой комнате"""
        self.client.login(username='roomparticipant', password='pass123')
        room = Room.objects.create(creator=self.user1, code='NOACCESS01')

        response = self.client.get(reverse('room_detail', args=['NOACCESS01']))
        self.assertEqual(response.status_code, 302)

    def test_leave_room_participant(self):
        """Участник покидает комнату"""
        room = Room.objects.create(creator=self.user1, participant=self.user2, code='LEAVE01')

        self.client.login(username='roomparticipant', password='pass123')
        response = self.client.post(reverse('leave_room', args=['LEAVE01']))

        self.assertEqual(response.status_code, 302)
        room.refresh_from_db()
        self.assertIsNone(room.participant)

    def test_leave_room_creator(self):
        """Создатель покидает комнату (комната деактивируется)"""
        room = Room.objects.create(creator=self.user1, code='CLOSE01')

        self.client.login(username='roomcreator', password='pass123')
        response = self.client.post(reverse('leave_room', args=['CLOSE01']))

        self.assertEqual(response.status_code, 302)
        room.refresh_from_db()
        self.assertFalse(room.is_active)

    def test_leave_room_get_redirects(self):
        """GET запрос на leave_room перенаправляет с ошибкой"""
        room = Room.objects.create(creator=self.user1, code='GET001')
        self.client.login(username='roomcreator', password='pass123')

        response = self.client.get(reverse('leave_room', args=['GET001']))

        self.assertEqual(response.status_code, 302)
        room.refresh_from_db()
        self.assertTrue(room.is_active)


class RoomAPITest(TestCase):
    """Тесты для API комнат"""

    def setUp(self):
        self.client = Client()
        self.user1 = CustomUser.objects.create_user(
            username='apiuser1',
            email='apiuser1@test.com',
            password='pass123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='apiuser2',
            email='apiuser2@test.com',
            password='pass123'
        )

    def test_check_room_exists(self):
        """Проверка существующей комнаты"""
        room = Room.objects.create(creator=self.user1, code='API001')
        self.client.login(username='apiuser1', password='pass123')

        response = self.client.get(reverse('check_room', args=['API001']))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['exists'])
        self.assertEqual(data['mode'], 'free')

    def test_check_room_not_exists(self):
        """Проверка несуществующей комнаты"""
        self.client.login(username='apiuser1', password='pass123')

        response = self.client.get(reverse('check_room', args=['INVALID']))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['exists'])

    def test_join_room_api_success(self):
        """API присоединения к комнате"""
        room = Room.objects.create(creator=self.user1, code='APIJOIN1')
        self.client.login(username='apiuser2', password='pass123')

        response = self.client.post(
            reverse('join_room_api'),
            data='{"room_code": "APIJOIN1"}',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['room_code'], 'APIJOIN1')

    def test_join_room_api_full(self):
        """API присоединения к полной комнате"""
        room = Room.objects.create(creator=self.user1, participant=self.user2, code='APIFULL1')
        stranger = CustomUser.objects.create_user(
            username='stranger',
            email='stranger@test.com',
            password='pass'
        )
        self.client.login(username='stranger', password='pass')

        response = self.client.post(
            reverse('join_room_api'),
            data='{"room_code": "APIFULL1"}',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])

    def test_get_messages(self):
        """Получение истории сообщений"""
        room = Room.objects.create(creator=self.user1, code='APIMSG01')
        ChatMessage.objects.create(room=room, user=self.user1, message='Test 1')
        ChatMessage.objects.create(room=room, user=self.user1, message='Test 2')

        self.client.login(username='apiuser1', password='pass123')
        response = self.client.get(reverse('get_messages', args=['APIMSG01']))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['messages']), 2)


class TurnModeTest(TestCase):
    """Тесты для режима 'По очереди'"""

    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username='player1',
            email='player1@test.com',
            password='pass123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='player2',
            email='player2@test.com',
            password='pass123'
        )

    def test_create_turn_mode_room(self):
        """Создание комнаты в режиме 'По очереди'"""
        room = Room.objects.create(
            creator=self.user1,
            mode='turn',
            max_turns=10
        )
        self.assertEqual(room.mode, 'turn')
        self.assertEqual(room.max_turns, 10)
        self.assertEqual(room.turn_count, 0)

    def test_get_current_drawer(self):
        """Определение текущего рисующего"""
        room = Room.objects.create(
            creator=self.user1,
            mode='turn',
            current_turn=self.user1,
            participant=self.user2
        )
        self.assertEqual(room.get_current_drawer(), self.user1)

        room.turn_count = 1
        self.assertEqual(room.get_current_drawer(), self.user2)

        room.turn_count = 2
        self.assertEqual(room.get_current_drawer(), self.user1)

    def test_next_turn(self):
        """Переход к следующему ходу"""
        room = Room.objects.create(
            creator=self.user1,
            mode='turn',
            current_turn=self.user1,
            participant=self.user2
        )

        room.next_turn()
        self.assertEqual(room.turn_count, 1)
        self.assertEqual(room.current_turn, self.user2)

        room.next_turn()
        self.assertEqual(room.turn_count, 2)
        self.assertEqual(room.current_turn, self.user1)

    def test_is_turn_mode_finished(self):
        """Проверка окончания режима 'По очереди'"""
        room = Room.objects.create(
            creator=self.user1,
            mode='turn',
            max_turns=5,
            turn_count=0
        )

        self.assertFalse(room.is_turn_mode_finished())

        room.turn_count = 4
        self.assertFalse(room.is_turn_mode_finished())

        room.turn_count = 5
        self.assertTrue(room.is_turn_mode_finished())
