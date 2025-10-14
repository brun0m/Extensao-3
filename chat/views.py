# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Chat
from django.http import JsonResponse

@login_required
def chat_home(request):
    """
    Página principal do chat, onde carregamos todos os chats do usuário.
    """
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/menu.html', {'chats': chats})

@login_required
def create_chat(request):
    if request.method == "POST":
        chat = Chat.objects.create(user=request.user, title=f"Chat {Chat.objects.filter(user=request.user).count() + 1}")
        return JsonResponse({
            "chat_id": chat.id,
            "title": chat.title
        })

@login_required
def chat_home(request):
    """
    Página principal do chat, onde carregamos todos os chats do usuário.
    """
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user/menu.html', {'chats': chats})


@login_required
def create_chat(request):
    """
    Cria um novo chat e retorna os dados em JSON.
    """
    if request.method == "POST":
        chat = Chat.objects.create(
            user=request.user,
            title=f"Chat {Chat.objects.filter(user=request.user).count() + 1}"
        )
        return JsonResponse({
            "chat_id": chat.id,
            "title": chat.title
        })
    return JsonResponse({"error": "Método inválido"}, status=400)


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    return render(request, 'user/menu.html', {'chat': chat})

@login_required
def chat_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    messages = chat.messages.order_by("created_at").values("sender", "text", "created_at")
    return JsonResponse({"messages": list(messages)})