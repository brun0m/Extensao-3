from django.db import models
from chat.models import Chat

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=50, default="AI")  # 'AI' ou 'User'
    text = models.TextField()  
    raw_response = models.JSONField(blank=True, null=True)  # salva JSON do Gemini
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


