from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path("new/", views.create_chat, name="create_chat"),
    path('<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('<int:chat_id>/messages/', views.chat_messages, name='chat_messages'),
]
