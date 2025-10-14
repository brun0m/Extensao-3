from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('processar_mensagem/<int:chat_id>/', views.processar_mensagem, name='processar_mensagem'),
]