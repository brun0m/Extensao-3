from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("transcrever/", views.transcrever, name="transcrever"),
    path("testar_gemini/", views.testar_gemini, name="testar_gemini"),
]