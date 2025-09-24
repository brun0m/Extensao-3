# views.py
from django.shortcuts import render
from django.http import JsonResponse
import whisper
import tempfile
from google import genai
import json
import re

# Configure Gemini 
client = genai.Client()

# URLs das APIs externas (Together, DeepInfra, Groq, etc.)
#TOGETHER_API_URL = "https://api.together.xyz/v1/models/mistral-7b"  # exemplo
#DEEPINFRA_API_URL = "https://api.deepinfra.com/v1/llm"  # exemplo
#GROQ_API_URL = "https://api.groq.com/v1/llm"  # exemplo
# Gemini é acessado via SDK (genai)

# views.py
model = whisper.load_model("base")  # Carrega o modelo uma vez

def home(request):
    return render(request, "core/generate_summary.html")

def testar_gemini(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            texto_reuniao = data.get("texto_reuniao", "")
            if not texto_reuniao.strip():
                return JsonResponse({"error": "Texto da reunião vazio."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)

        prompt = f"""
Você é um analista de requisitos experiente.
Recebendo o seguinte texto de reunião com o cliente:
\"\"\"{texto_reuniao}\"\"\"

- Liste os requisitos funcionais e não funcionais.
- Crie histórias de usuário seguindo o formato:
"Como [usuário], eu quero [ação], para [benefício]".
- Crie critérios de aceitação claros para cada história.
- Escreva em português.
- Responda apenas com as informações solicitadas, sem explicações adicionais.
"""

        # Chamada para Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        texto_gerado = response.text
        texto_formatado = formatar_requisitos(texto_gerado)

        return JsonResponse({
            "requisitos": texto_formatado
        }, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({"error": "Método não permitido."}, status=405)


def formatar_requisitos(texto):
    # Substitui cabeçalhos em Markdown por títulos HTML
    texto = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', texto)
    # Converte listas Markdown em listas HTML
    texto = re.sub(r'^\*   (.*)$', r'• \1', texto, flags=re.MULTILINE)
    return texto

def transcrever(request):
    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]

        # Salva temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        # Transcreve com Whisper
        result = model.transcribe(tmp_path, language="pt")
        return JsonResponse({"texto": result["text"]})

    return JsonResponse({"error": "Nenhum áudio enviado."}, status=400)












