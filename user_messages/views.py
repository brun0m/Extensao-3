# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chat.models import Chat
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from django.http import FileResponse
from io import BytesIO
    
# View para retornar histórico de mensagens de um chat
def get_chat_messages(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
    except Chat.DoesNotExist:
        return JsonResponse({"error": "Chat não encontrado."}, status=404)

    messages = chat.messages.order_by("created_at").values("id", "sender", "text", "created_at")
    messages_list = list(messages)
    return JsonResponse({"messages": messages_list})


@csrf_exempt
def gerar_pdf(request, chat_id):
    chat = Chat.objects.get(id=chat_id, user=request.user)
    last_ai_message = chat.messages.filter(sender="AI").last()

    if not last_ai_message:
        return JsonResponse({"error": "Nenhuma mensagem da IA encontrada."}, status=400)

    # Extrair o JSON do texto da IA
    texto = last_ai_message.text.strip()
    json_inicio = texto.find('{')
    json_fim = texto.rfind('}') + 1
    if json_inicio == -1 or json_fim == -1:
        return JsonResponse({"error": "Nenhum JSON válido encontrado na mensagem."}, status=400)

    try:
        dados = json.loads(texto[json_inicio:json_fim])
    except json.JSONDecodeError:
        return JsonResponse({"error": "Falha ao decodificar o JSON dos requisitos."}, status=400)

    # Criação do PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name='CustomHeading1', fontSize=16, spaceAfter=10, leading=20, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='CustomHeading2', fontSize=14, spaceAfter=8, leading=18, alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Body', fontSize=12, leading=16))

    story = []

    story.append(Paragraph("📘 Documentação de Requisitos", styles["CustomHeading1"]))
    story.append(Spacer(1, 12))

    # Requisitos Funcionais
    story.append(Paragraph("🔹 Requisitos Funcionais", styles["CustomHeading2"]))
    rf_itens = [ListItem(Paragraph(f"<b>{r['id']}</b> - {r['descricao']}", styles["Body"])) for r in dados.get("requisitos_funcionais", [])]
    story.append(ListFlowable(rf_itens, bulletType='bullet'))
    story.append(Spacer(1, 12))

    # Requisitos Não Funcionais
    story.append(Paragraph("🔸 Requisitos Não Funcionais", styles["CustomHeading2"]))
    rnf_itens = [ListItem(Paragraph(f"<b>{r['id']}</b> - {r['descricao']} <i>({r.get('observacao','')})</i>", styles["Body"])) for r in dados.get("requisitos_nao_funcionais", [])]
    story.append(ListFlowable(rnf_itens, bulletType='bullet'))
    story.append(Spacer(1, 12))

    # Casos de Uso
    story.append(Paragraph("🎯 Casos de Uso", styles["CustomHeading2"]))
    cu_itens = [ListItem(Paragraph(f"<b>{r['id']}</b> ({r['ator']}): {r['descricao']}", styles["Body"])) for r in dados.get("casos_de_uso", [])]
    story.append(ListFlowable(cu_itens, bulletType='bullet'))
    story.append(Spacer(1, 12))

    # Histórias de Usuário
    story.append(Paragraph("👥 Histórias de Usuário", styles["CustomHeading2"]))
    hu_itens = [ListItem(Paragraph(f"{r}", styles["Body"])) for r in dados.get("historias_usuario", [])]
    story.append(ListFlowable(hu_itens, bulletType='bullet'))
    story.append(Spacer(1, 12))

    # Backlog
    story.append(Paragraph("📋 Backlog do Projeto", styles["CustomHeading2"]))
    backlog = dados.get("backlog", {})
    for cat in ["must", "should", "could", "wont"]:
        if backlog.get(cat):
            story.append(Paragraph(f"<b>{cat.capitalize()}:</b>", styles["Body"]))
            itens = [ListItem(Paragraph(i, styles["Body"])) for i in backlog[cat]]
            story.append(ListFlowable(itens, bulletType='bullet'))
            story.append(Spacer(1, 6))

    doc.build(story)
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="documentacao_requisitos.pdf")