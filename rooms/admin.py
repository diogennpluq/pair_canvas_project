from django.contrib import admin
from .models import Room, ChatMessage, Drawing

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['code', 'creator', 'participant', 'mode', 'is_active', 'created_at']
    list_filter = ['mode', 'is_active', 'created_at']
    search_fields = ['code', 'creator__username', 'participant__username']
    readonly_fields = ['created_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['room', 'user', 'message_preview', 'timestamp']
    list_filter = ['room', 'user', 'timestamp']
    search_fields = ['message', 'user__username']
    readonly_fields = ['timestamp']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Сообщение'

@admin.register(Drawing)
class DrawingAdmin(admin.ModelAdmin):
    list_display = ['room', 'created_by', 'created_at']
    list_filter = ['room', 'created_by', 'created_at']
    readonly_fields = ['created_at']