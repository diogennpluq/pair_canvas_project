from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room

def home(request):
    """Главная страница"""
    return render(request, 'rooms/home.html')

@login_required
def create_room(request):
    """Создание новой комнаты"""
    if request.method == 'POST':
        mode = request.POST.get('mode', 'free')
        max_turns = request.POST.get('max_turns', '10')

        # Создаем комнату
        room = Room.objects.create(
            creator=request.user,
            mode=mode,
            max_turns=int(max_turns) if str(max_turns).isdigit() else 10,
        )

        # Для режима "По очереди" устанавливаем текущий ход
        if mode == 'turn':
            room.current_turn = request.user
            room.save(update_fields=['current_turn'])

        messages.success(request, f'Комната создана! Код: {room.code}')
        return redirect('room_detail', room_code=room.code)

    return render(request, 'rooms/create_room.html')

@login_required
def join_room(request):
    """Присоединение к комнате по коду"""
    if request.method == 'POST':
        room_code = request.POST.get('room_code', '').upper()
        
        try:
            room = Room.objects.get(code=room_code, is_active=True)
            
            if room.participant is None:
                room.participant = request.user
                room.save()
                messages.success(request, f'Вы присоединились к комнате {room.code}')
                return redirect('room_detail', room_code=room.code)
            else:
                messages.error(request, 'Комната уже заполнена')
        except Room.DoesNotExist:
            messages.error(request, 'Комната не найдена')
    
    return render(request, 'rooms/join_room.html')

@login_required
def room_detail(request, room_code):
    """Детальная страница комнаты"""
    room = get_object_or_404(Room, code=room_code)

    # Проверяем, имеет ли пользователь доступ к комнате
    if not room.is_user_in_room(request.user):
        messages.error(request, 'У вас нет доступа к этой комнате')
        return redirect('home')

    # Получаем пользователей в комнате
    users_in_room = room.get_users()

    # Определяем, чей сейчас ход (для режима "По очереди")
    is_current_drawer = False
    if room.mode == 'turn':
        is_current_drawer = room.current_turn == request.user if room.current_turn else False

    context = {
        'room': room,
        'users_in_room': users_in_room,
        'is_creator': request.user == room.creator,
        'websocket_url': f'ws://{request.get_host()}/ws/room/{room.code}/',
        'is_current_drawer': is_current_drawer,
    }

    return render(request, 'rooms/room_detail.html', context)

@login_required
def leave_room(request, room_code):
    """Выход из комнаты"""
    if request.method != 'POST':
        messages.error(request, 'Некорректный запрос')
        return redirect('home')
    
    room = get_object_or_404(Room, code=room_code)

    if request.user == room.participant:
        room.participant = None
        room.save()
        messages.success(request, 'Вы покинули комнату')
    elif request.user == room.creator:
        # Если создатель выходит - закрываем комнату
        room.is_active = False
        room.save()
        messages.success(request, 'Вы закрыли комнату')

    return redirect('home')