from django.db import models
from django.conf import settings
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
    
    def __str__(self):
        return f"Комната {self.code} ({self.get_mode_display()})"
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Генерируем уникальный код комнаты
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
    image_data = models.TextField()  # Храним как base64
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Рисунок из комнаты {self.room.code}"