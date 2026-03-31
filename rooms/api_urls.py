from django.urls import path
from . import api_views

urlpatterns = [
    path('check_room/<str:room_code>/', api_views.check_room, name='check_room'),
    path('join_room_api/', api_views.join_room_api, name='join_room_api'),
    path('leave_room_api/<str:room_code>/', api_views.leave_room_api, name='leave_room_api'),
    path('get_messages/<str:room_code>/', api_views.get_messages, name='get_messages'),

    # Endpoints для режима "По очереди"
    path('get_state/<str:room_code>/', api_views.get_room_state, name='get_room_state'),
    path('next_turn/<str:room_code>/', api_views.next_turn, name='next_turn'),
]