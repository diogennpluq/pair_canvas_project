from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rooms.models import Drawing

@login_required
def gallery(request):
    """Страница галереи рисунков"""
    # Получаем рисунки пользователя
    user_drawings = Drawing.objects.filter(created_by=request.user).order_by('-created_at')
    
    # Получаем последние рисунки всех пользователей
    recent_drawings = Drawing.objects.all().order_by('-created_at')[:20]
    
    context = {
        'user_drawings': user_drawings,
        'recent_drawings': recent_drawings,
    }
    
    return render(request, 'gallery/gallery.html', context)