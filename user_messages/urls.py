from django.urls import path
from . import views

urlpatterns = [
    path('get_chat_messages/<int:chat_id>/', views.get_chat_messages, name='get_chat_messages'),
]