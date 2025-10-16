from django.urls import path
from . import views

urlpatterns = [
    path('get_chat_messages/<int:chat_id>/', views.get_chat_messages, name='get_chat_messages'),
    path("gerar_pdf/<int:chat_id>/", views.gerar_pdf, name="gerar_pdf"),
]