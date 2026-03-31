from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rooms.models import Room, Drawing

CustomUser = get_user_model()


class GalleryViewTest(TestCase):
    """Тесты для представления галереи"""

    def setUp(self):
        self.client = Client()
        self.user1 = CustomUser.objects.create_user(
            username='galleryuser1',
            email='galleryuser1@test.com',
            password='pass123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='galleryuser2',
            email='galleryuser2@test.com',
            password='pass123'
        )
        self.room = Room.objects.create(creator=self.user1, code='GAL001')
        self.gallery_url = reverse('gallery')

    def test_gallery_requires_login(self):
        """Галерея требует авторизации"""
        response = self.client.get(self.gallery_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_gallery_get(self):
        """GET запрос к странице галереи"""
        self.client.login(username='galleryuser1', password='pass123')
        response = self.client.get(self.gallery_url)
        self.assertEqual(response.status_code, 200)
        # Проверяем что используется шаблон gallery.html
        self.assertTemplateUsed(response, 'gallery/gallery.html')

    def test_gallery_user_drawings_empty(self):
        """Галерея пользователя пуста если нет рисунков"""
        self.client.login(username='galleryuser1', password='pass123')
        response = self.client.get(self.gallery_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['user_drawings']), 0)

    def test_gallery_user_drawings_with_drawings(self):
        """Галерея пользователя содержит рисунки"""
        # Создаем рисунки от имени пользователя
        Drawing.objects.create(
            room=self.room,
            image_data='base64_data_1',
            created_by=self.user1
        )
        Drawing.objects.create(
            room=self.room,
            image_data='base64_data_2',
            created_by=self.user1
        )
        
        self.client.login(username='galleryuser1', password='pass123')
        response = self.client.get(self.gallery_url)
        
        self.assertEqual(len(response.context['user_drawings']), 2)

    def test_gallery_recent_drawings(self):
        """Галерея показывает последние рисунки"""
        # Создаем несколько рисунков от разных пользователей
        for i in range(25):
            Drawing.objects.create(
                room=self.room,
                image_data=f'base64_data_{i}',
                created_by=self.user1 if i % 2 == 0 else self.user2
            )
        
        self.client.login(username='galleryuser1', password='pass123')
        response = self.client.get(self.gallery_url)
        
        # Должно быть не более 20 последних
        self.assertLessEqual(len(response.context['recent_drawings']), 20)

    def test_gallery_user_drawings_ordering(self):
        """Рисунки пользователя сортируются по убыванию даты"""
        drawing1 = Drawing.objects.create(
            room=self.room,
            image_data='older',
            created_by=self.user1
        )
        drawing2 = Drawing.objects.create(
            room=self.room,
            image_data='newer',
            created_by=self.user1
        )
        
        self.client.login(username='galleryuser1', password='pass123')
        response = self.client.get(self.gallery_url)
        
        user_drawings = list(response.context['user_drawings'])
        # Новый рисунок должен быть первым
        self.assertEqual(user_drawings[0].image_data, 'newer')
        self.assertEqual(user_drawings[1].image_data, 'older')

    def test_gallery_different_users_drawings(self):
        """Пользователи видят только свои рисунки в user_drawings"""
        # Пользователь 1 создает рисунок
        Drawing.objects.create(
            room=self.room,
            image_data='user1_drawing',
            created_by=self.user1
        )
        # Пользователь 2 создает рисунок
        Drawing.objects.create(
            room=self.room,
            image_data='user2_drawing',
            created_by=self.user2
        )
        
        # Пользователь 1 видит только свой рисунок
        self.client.login(username='galleryuser1', password='pass123')
        response = self.client.get(self.gallery_url)
        
        user_drawings = response.context['user_drawings']
        self.assertEqual(len(user_drawings), 1)
        self.assertEqual(user_drawings[0].image_data, 'user1_drawing')
