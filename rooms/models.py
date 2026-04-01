from django.db import models, transaction
from django.db.models import F
from django.conf import settings
from django.contrib.auth import get_user_model
import random
import string

class Room(models.Model):
    MODE_CHOICES = [
        ('free', 'Свободное рисование'),
        ('turn', 'По очереди'),
        ('mirror', 'Зеркало'),
    ]

    code = models.CharField(max_length=8, unique=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_rooms')
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='joined_rooms')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    current_turn = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_turn_rooms')

    # Поля для режима "По очереди"
    turn_count = models.IntegerField(default=0)  # Количество сделанных ходов
    max_turns = models.IntegerField(default=10)  # Максимальное количество ходов

    def __str__(self):
        return f"Комната {self.code} ({self.get_mode_display()})"

    def save(self, *args, **kwargs):
        """Генерируем уникальный код комнаты только при создании"""
        if not self.code and self._state.adding:
            # Генерируем уникальный код комнаты только для новых объектов
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)

    def has_space(self):
        """Проверяем, есть ли место для второго участника"""
        return self.participant is None and self.is_active

    def get_users(self):
        """Возвращает список пользователей в комнате"""
        users = [self.creator]
        if self.participant:
            users.append(self.participant)
        return users

    def is_user_in_room(self, user):
        """Проверяет, находится ли пользователь в комнате"""
        return user == self.creator or user == self.participant

    def get_current_drawer(self):
        """Возвращает пользователя, чей сейчас ход (для режима 'По очереди')"""
        if self.turn_count % 2 == 0:
            return self.creator
        return self.participant if self.participant else self.creator

    def next_turn(self):
        """Переход к следующему ходу"""
        self.turn_count += 1
        self.current_turn = self.get_current_drawer()
        if self.pk:  # Только если объект уже сохранён
            self.save(update_fields=['turn_count', 'current_turn'])

    def is_turn_mode_finished(self):
        """Проверяет, закончилась ли игра в режиме 'По очереди'"""
        return self.turn_count >= self.max_turns

    def reset_turn_mode(self):
        """Сброс режима 'По очереди' для новой игры"""
        self.turn_count = 0
        self.current_turn = self.creator
        self.save(update_fields=['turn_count', 'current_turn'])

class ChatMessage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}..."


class Drawing(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='drawings')
    image = models.ImageField(upload_to='drawings/%Y/%m/%d/', blank=True, null=True)
    image_data = models.TextField(blank=True, default='')  # Храним как base64 для обратной совместимости
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Рисунок'
        verbose_name_plural = 'Рисунки'

    def __str__(self):
        return f"Рисунок из комнаты {self.room.code}"

    def save(self, *args, **kwargs):
        # Обновляем счётчик рисунков пользователя только при первом создании
        is_new = self._state.adding
        if is_new and self.created_by_id:
            # Обновляем счётчик атомарно с использованием F-выражений
            with transaction.atomic():
                User = get_user_model()
                User.objects.filter(pk=self.created_by_id).update(
                    drawings_count=F('drawings_count') + 1,
                    score=F('score') + 10
                )
        super().save(*args, **kwargs)