# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chat.models import Chat
from user_messages.models import Message
from core.views import processar_mensagem
    
# View para retornar histórico de mensagens de um chat
def get_chat_messages(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
    except Chat.DoesNotExist:
        return JsonResponse({"error": "Chat não encontrado."}, status=404)

    messages = chat.messages.order_by("created_at").values("id", "sender", "text", "created_at")
    messages_list = list(messages)
    return JsonResponse({"messages": messages_list})