document.addEventListener('DOMContentLoaded', () => {

let currentChatId = null;
let mediaRecorder;
let audioChunks = [];

// Selecionar um chat
document.querySelectorAll('.chat-item').forEach(item => {
    item.addEventListener('click', async () => {
        document.querySelectorAll('.chat-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        currentChatId = item.dataset.chatId;
        await loadChatMessages(currentChatId);
    });
});

// Carregar histórico
async function loadChatMessages(chatId) {
    const container = document.getElementById('messages-container');
    container.innerHTML = '';

    try {
        const res = await fetch(`/chat/${chatId}/messages/`);
        if (!res.ok) throw new Error(`Erro ${res.status}`);
        const data = await res.json();

        if (!data.messages || data.messages.length === 0) {
            container.innerHTML = `<div class="no-chat-message">Nenhuma mensagem ainda</div>`;
            return;
        }

        data.messages.forEach(msg => {
            appendMessage(msg.sender.toLowerCase() === 'user' ? 'user' : 'ai', msg.text);
        });

        container.scrollTop = container.scrollHeight;

    } catch (err) {
        console.error("Erro ao carregar mensagens:", err);
        container.innerHTML = `<div class="no-chat-message">Erro ao carregar mensagens.</div>`;
    }
}

// Enviar mensagem de texto
document.getElementById('send-btn').addEventListener('click', async () => {
    const input = document.getElementById('message-input');
    const mensagem = input.value.trim();
    if (!mensagem || !currentChatId) return;

    try {
        const res = await fetch(`/processar_mensagem/${currentChatId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ mensagem })
        });
        const data = await res.json();

        appendMessage('user', data.user_message);   // Usuário
        appendMessage('ai', data.ai_message);       // IA (HTML bonito)

        input.value = '';

    } catch (err) {
        console.error("Erro ao enviar mensagem:", err);
    }
});

// Gravação de áudio
document.getElementById('record-btn').addEventListener('click', () => {
    if (!mediaRecorder || mediaRecorder.state === "inactive") startRecording();
    else stopRecording();
});

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            audioChunks = [];
            document.getElementById('record-btn').textContent = '🛑 Gravando...';

            mediaRecorder.addEventListener("dataavailable", e => audioChunks.push(e.data));
            mediaRecorder.addEventListener("stop", sendAudio);
        });
}

function stopRecording() {
    mediaRecorder.stop();
    document.getElementById('record-btn').textContent = '🎙️';
}

async function sendAudio() {
    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append("audio", blob, "recording.webm");

    try {
        const res = await fetch(`/processar_mensagem/${currentChatId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            body: formData
        });

        const data = await res.json();
        appendMessage('user', '(áudio enviado)');
        appendMessage('ai', data.ai_message);

    } catch (err) {
        console.error("Erro ao enviar áudio:", err);
    } finally {
        document.getElementById('record-btn').textContent = '🎙️';
    }
}

// Adicionar mensagem ao container
function appendMessage(sender, text) {
    const container = document.getElementById('messages-container');
    const div = document.createElement('div');
    div.classList.add('message', sender);
    div.innerHTML = text;
    container.appendChild(div);

    // Se a mensagem for da IA, adiciona o botão logo abaixo dela
    if (sender === 'ai') {
        const btn = document.createElement('button');
        btn.textContent = "📄 Exportar para PDF";
        btn.classList.add('pdf-btn');
        btn.onclick = () => gerarPDF(currentChatId);

        const wrapper = document.createElement('div');
        wrapper.classList.add('pdf-btn-container');
        wrapper.appendChild(btn);
        container.appendChild(wrapper);
    }

    container.scrollTop = container.scrollHeight;
}

if (data.ai_message) {
    appendMessage('ai', formatAIResponse(data.ai_message));

    // Adiciona o botão de gerar PDF abaixo da última resposta
    const container = document.getElementById('messages-container');
    const btn = document.createElement('button');
    btn.textContent = "📄 Gerar PDF";
    btn.classList.add('pdf-btn');
    btn.onclick = () => gerarPDF(currentChatId);
    container.appendChild(btn);
}

async function gerarPDF(chatId) {
    try {
        const res = await fetch(`user_messages/gerar_pdf/${chatId}/`);
        if (!res.ok) throw new Error("Erro ao gerar PDF.");

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "documentacao_requisitos.pdf";
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        alert("Erro ao gerar PDF. Veja o console.");
        console.error(err);
    }
}

// Pega cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

});



