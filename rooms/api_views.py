from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Room, ChatMessage, Drawing
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


@login_required
def get_room_state(request, room_code):
    """Получение текущего состояния комнаты (для синхронизации)"""
    try:
        room = Room.objects.get(code=room_code)

        data = {
            'mode': room.mode,
            'turn_count': room.turn_count,
            'max_turns': room.max_turns,
            'is_turn_mode_finished': room.is_turn_mode_finished(),
        }

        if room.mode == 'turn':
            data.update({
                'current_drawer': room.current_turn.username if room.current_turn else None,
                'is_current_drawer': room.current_turn == request.user if room.current_turn else False,
            })

        return JsonResponse(data)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Комната не найдена'}, status=404)


@login_required
@require_http_methods(["POST"])
def next_turn(request, room_code):
    """Переход к следующему ходу (для режима 'По очереди')"""
    try:
        room = Room.objects.get(code=room_code, mode='turn')

        # Проверка: только текущий рисующий может завершить ход
        if not room.current_turn or room.current_turn != request.user:
            return JsonResponse({'error': 'Не ваш ход'}, status=403)

        room.next_turn()

        # Отправляем уведомление через WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        room_group_name = f'room_{room.code}'
        
        async_to_sync(channel_layer.group_send)(
            room_group_name,
            {
                'type': 'game_state_update',
                'data': {
                    'turn_count': room.turn_count,
                    'max_turns': room.max_turns,
                    'is_current_drawer': room.current_turn == request.user if room.current_turn else False,
                    'current_drawer': room.current_turn.username if room.current_turn else None,
                    'is_finished': room.is_turn_mode_finished()
                }
            }
        )

        return JsonResponse({
            'success': True,
            'turn_count': room.turn_count,
            'current_drawer': room.current_turn.username if room.current_turn else None,
            'is_finished': room.is_turn_mode_finished()
        })
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Комната не найдена'}, status=404)
