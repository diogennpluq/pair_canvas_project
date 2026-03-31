from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views
from rooms import views as rooms_views
from gallery import views as gallery_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Аутентификация
    path('register/', accounts_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', accounts_views.profile, name='profile'),
    
    # Комнаты
    path('', rooms_views.home, name='home'),
    path('create_room/', rooms_views.create_room, name='create_room'),
    path('join_room/', rooms_views.join_room, name='join_room'),
    path('room/<str:room_code>/', rooms_views.room_detail, name='room_detail'),
    path('room/<str:room_code>/leave/', rooms_views.leave_room, name='leave_room'),
    
    # Галерея
    path('gallery/', gallery_views.gallery, name='gallery'),
    
    # API
    path('api/', include('rooms.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)