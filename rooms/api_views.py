from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Room, ChatMessage
import json

@login_required
def check_room(request, room_code):
    """Проверяет существование комнаты и доступность"""
    try:
        room = Room.objects.get(code=room_code, is_active=True)
        return JsonResponse({
            'exists': True,
            'has_space': room.has_space(),
            'mode': room.mode,
            'creator': room.creator.username
        })
    except Room.DoesNotExist:
        return JsonResponse({'exists': False})

@login_required
def join_room_api(request):
    """API для присоединения к комнате"""
    if request.method == 'POST':
        data = json.loads(request.body)
        room_code = data.get('room_code')
        
        try:
            room = Room.objects.get(code=room_code, is_active=True)
            
            if room.participant is None:
                room.participant = request.user
                room.save()
                return JsonResponse({
                    'success': True,
                    'room_code': room.code,
                    'mode': room.mode
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Комната уже заполнена'
                })
        except Room.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Комната не найдена'
            })

@login_required
def leave_room_api(request, room_code):
    """API для выхода из комнаты"""
    try:
        room = Room.objects.get(code=room_code)
        
        if request.user == room.participant:
            room.participant = None
            room.is_active = False
            room.save()
        elif request.user == room.creator:
            # Если создатель выходит - закрываем комнату
            room.is_active = False
            room.save()
        
        return JsonResponse({'success': True})
    except Room.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Комната не найдена'})

@login_required
def get_messages(request, room_code):
    """Получение истории сообщений комнаты"""
    try:
        room = Room.objects.get(code=room_code)
        messages = ChatMessage.objects.filter(room=room).order_by('timestamp')[:50]
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'user': msg.user.username,
                'message': msg.message,
                'timestamp': msg.timestamp.strftime('%H:%M')
            })
        
        return JsonResponse({'messages': messages_data})
    except Room.DoesNotExist:
        return JsonResponse({'messages': []})