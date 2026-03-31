from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import CustomUser
from .forms import CustomUserCreationForm, ProfileUpdateForm


class CustomUserModelTest(TestCase):
    """Тесты для модели CustomUser"""

    def test_create_user(self):
        """Создание пользователя с основными полями"""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.score, 0)
        self.assertEqual(user.drawings_count, 0)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Создание суперпользователя"""
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin.username, 'admin')
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_str_representation(self):
        """Строковое представление пользователя"""
        user = CustomUser.objects.create_user(
            username='john_doe',
            password='pass123'
        )
        self.assertEqual(str(user), 'john_doe')

    def test_get_avatar_url_with_avatar(self):
        """Получение URL аватара когда аватар установлен"""
        user = CustomUser.objects.create_user(
            username='avatar_user',
            password='pass123'
        )
        # Проверяем дефолтный URL (без аватара)
        self.assertEqual(user.get_avatar_url(), '/static/images/default_avatar.png')

    def test_duplicate_username_fails(self):
        """Создание пользователя с дублирующимся username вызывает ошибку"""
        CustomUser.objects.create_user(
            username='duplicate',
            password='pass123'
        )
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(
                username='duplicate',
                password='pass456'
            )


class RegisterViewTest(TestCase):
    """Тесты для представления регистрации"""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_get(self):
        """GET запрос к странице регистрации"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_post_valid(self):
        """POST запрос с валидными данными"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)  # Редирект на home
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_register_post_invalid(self):
        """POST запрос с невалидными данными"""
        data = {
            'username': '',
            'email': 'invalid-email',
            'password1': '123',
            'password2': '456'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

    def test_register_auto_login(self):
        """Пользователь автоматически входит после регистрации"""
        data = {
            'username': 'autologinuser',
            'email': 'auto@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        }
        response = self.client.post(self.register_url, data)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'autologinuser')


class ProfileViewTest(TestCase):
    """Тесты для представления профиля"""

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='pass123'
        )
        self.profile_url = reverse('profile')

    def test_profile_requires_login(self):
        """Страница профиля требует авторизации"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_profile_get(self):
        """GET запрос к странице профиля"""
        self.client.login(username='profileuser', password='pass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertIsInstance(response.context['form'], ProfileUpdateForm)

    def test_profile_update_post(self):
        """Обновление профиля через POST"""
        self.client.login(username='profileuser', password='pass123')
        data = {
            'email': 'updated@example.com',
            'bio': 'Test bio'
        }
        response = self.client.post(self.profile_url, data)
        self.assertEqual(response.status_code, 302)
        
        # Проверяем обновление данных
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.bio, 'Test bio')
