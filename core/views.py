from django.shortcuts import render
from django.http import JsonResponse
import whisper
from google import genai
from django.views.decorators.csrf import csrf_exempt
from chat.models import Chat
from user_messages.models import Message
import json, tempfile, os, time, re
from google.genai.errors import ServerError
import spacy
from spellchecker import SpellChecker
import nltk
from difflib import get_close_matches
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
load_dotenv()

#/specify "Criar uma API REST para gerenciar tarefas. Usuários podem criar, listar, atualizar e deletar tarefas. Cada tarefa tem título, descrição e status (pendente/concluída)."
#/constitution "Usar Python 3.12, FastAPI, banco SQLite, testes com PyTest, PEP8 como padrão de código."
#/plan "Criar modelos ORM para Tarefa, rotas CRUD, endpoints REST, autenticação básica com token, testes unitários para cada rota."

# Configura Gemini 
client = genai.Client()
#nltk.download('punkt')

# Modelo Whisper
model = whisper.load_model("small")  

# spaCy
nlp = spacy.load("pt_core_news_sm")

@login_required 
def menu(request):
    user = request.user  # usuário logado
    chats = Chat.objects.filter(user_id=user)
    print(f"Usuário logado: {user.username} (id={user.id})")
    print(f"Chats encontrados: {chats.count()}")
    return render(request, 'user/menu.html', {'chats': chats})


def carregar_glossario(caminho_json): 
    with open(caminho_json, "r", encoding="utf-8") as f:
        return json.load(f)

def normalizar_texto(texto, glossario, cutoff=0.9):
    spell = SpellChecker(language='pt')
    # Aqui você pode usar spaCy se quiser
    palavras = texto.split()
    palavras_normalizadas = []

    for palavra in palavras:
        substituido = False
        for informal, tecnico in glossario.items():
            if palavra.lower() == informal.lower():
                palavras_normalizadas.append(tecnico)
                substituido = True
                break
        if not substituido:
            palavras_normalizadas.append(palavra)

    return " ".join(palavras_normalizadas)

def formatar_requisitos(texto):
    """Recebe JSON string e gera HTML bonito"""
    try:
        json_data = json.loads(texto)
    except:
        return texto  # fallback se não for JSON

    html = ""

    html += "<h4>🧩 Requisitos Funcionais</h4><ul>"
    for r in json_data.get("requisitos_funcionais", []):
        html += f"<li><b>{r.get('id')}:</b> {r.get('descricao')}</li>"
    html += "</ul>"

    html += "<h4>⚙️ Requisitos Não Funcionais</h4><ul>"
    for r in json_data.get("requisitos_nao_funcionais", []):
        html += f"<li><b>{r.get('id')}:</b> {r.get('descricao')} ({r.get('observacao', '')})</li>"
    html += "</ul>"

    html += "<h4>🎭 Casos de Uso</h4><ul>"
    for c in json_data.get("casos_de_uso", []):
        html += f"<li><b>{c.get('id')}:</b> {c.get('descricao')}</li>"
    html += "</ul>"

    html += "<h4>👥 Histórias de Usuário</h4><ul>"
    for h in json_data.get("historias_usuario", []):
        html += f"<li>{h}</li>"
    html += "</ul>"

    html += "<h4>📋 Backlog</h4>"
    backlog = json_data.get("backlog", {})
    for key in backlog:
        html += f"<b>{key.upper()}</b>: {', '.join(backlog[key]) or '(vazio)'}<br>"

    return html

def limpar_json_llm(texto):
    """
    Remove crases, markdown e qualquer prefixo do LLM
    """
    # Remove ```json e ``` ou ```
    texto = re.sub(r"^```json\s*", "", texto.strip())
    texto = re.sub(r"^```\s*", "", texto.strip())
    texto = re.sub(r"```\s*$", "", texto.strip())

    # Remove espaços extras no começo/fim
    texto = texto.strip()
    
    # Garantir que é JSON válido
    try:
        json_obj = json.loads(texto)
        return json_obj
    except:
        # fallback: retorna como string mesmo
        return texto

@csrf_exempt
def processar_mensagem(request, chat_id):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido."}, status=405)

    chat = Chat.objects.get(id=chat_id, user=request.user)

    # === Captura do texto ===
    if request.FILES.get("audio"):
        audio_file = request.FILES["audio"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        result = model.transcribe(tmp_path, language="pt")
        texto_usuario = result["text"]
    else:
        try:
            data = json.loads(request.body)
            texto_usuario = data.get("mensagem", "").strip()
            if not texto_usuario:
                return JsonResponse({"error": "Mensagem vazia."}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)

    # Salva mensagem do usuário
    user_msg = Message.objects.create(chat=chat, sender="User", text=texto_usuario)

    # === Processamento LLM ===
    glossario = carregar_glossario(os.getenv("GLOSSARIO_PATH"))
    texto_normalizado = normalizar_texto(texto_usuario, glossario)
    prompt = criar_prompt(texto_normalizado)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
    except:
        time.sleep(5)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

    texto_gerado = response.text  # JSON puro da LLM

    json_gerado = limpar_json_llm(texto_gerado)

    # === Salva AI message ===
    ai_msg = Message.objects.create(
        chat=chat,
        sender="AI",
        text=formatar_requisitos(json.dumps(json_gerado, ensure_ascii=False)),  # HTML bonito
        raw_response={"json": json_gerado}  # JSON puro
    )

    return JsonResponse({
        "user_message": user_msg.text,
        "ai_message": ai_msg.text,      # HTML bonito para front
        "ai_raw": ai_msg.raw_response    # JSON puro
    }, json_dumps_params={'ensure_ascii': False})

#Pode aplicar Engenharia de Prompt se quiser
def criar_prompt(texto_normalizado):
 
        return f"""
Você é um analista de requisitos de software sênior, especializado em interpretar reuniões com clientes e transformar suas falas em especificações técnicas estruturadas.

Sua tarefa é extrair e organizar os requisitos a partir do texto abaixo, que é uma transcrição automática de uma reunião com o cliente.

A transcrição pode conter erros do Whisper (palavras trocadas, truncadas ou confusas) **e o cliente pode não ter conhecimento técnico**.  
Portanto:
- Interprete descrições informais e transforme-as em requisitos técnicos compreensíveis.
- Quando o cliente falar de forma vaga, interprete a intenção.
- Corrija pequenos erros de linguagem, mas preserve o sentido.

**Instruções importantes:**
1. Corrija erros de transcrição e traduza ideias vagas para linguagem técnica.
2. Retorne apenas um **JSON válido**, sem explicações adicionais.
3. Use o formato exato abaixo, com listas mesmo que vazias.
4. Mantenha a numeração sequencial de cada requisito.

Exemplo de estrutura esperada:
{{
  "requisitos_funcionais": [
    {{"id": "RF01", "descricao": "O sistema deve permitir o cadastro de clientes."}}
  ],
  "requisitos_nao_funcionais": [
    {{"id": "RNF01", "descricao": "O sistema deve estar disponível 24 horas por dia.", "observacao": "Alta disponibilidade"}}
  ],
  "casos_de_uso": [
    {{"id": "UC01", "ator": "Cliente", "descricao": "Cadastrar um novo cliente no sistema."}}
  ],
  "historias_usuario": [
    "Como cliente, quero poder cadastrar meus dados, para que o sistema armazene minhas informações de forma segura."
  ],
  "backlog": {{
    "must": ["Cadastro de clientes", "Autenticação de usuários"],
    "should": ["Relatório de clientes"],
    "could": ["Integração com planilhas"],
    "wont": ["Aplicativo mobile nesta fase"]
  }}
}}

Agora analise o seguinte texto e produza o JSON de requisitos:

Texto da reunião:
\"\"\"{texto_normalizado}\"\"\"
"""
