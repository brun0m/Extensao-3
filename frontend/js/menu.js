document.addEventListener("DOMContentLoaded", () => {
    let currentChatId = null;
    let mediaRecorder;
    let audioChunks = [];

    // ========= SELECIONAR CHAT =========
    document.querySelectorAll(".chat-item").forEach(item => {
        item.addEventListener("click", async () => {
            document.querySelectorAll(".chat-item").forEach(i => i.classList.remove("active"));
            item.classList.add("active");
            currentChatId = item.dataset.chatId;
            await loadChatMessages(currentChatId);
        });
    });

    // ========= CARREGAR HISTÓRICO =========
    async function loadChatMessages(chatId) {
        const container = document.getElementById("messages-container");
        container.innerHTML = "";

        try {
            const res = await fetch(`/chat/${chatId}/messages/`);
            if (!res.ok) throw new Error(`Erro ${res.status}`);

            const data = await res.json();
            if (!data.messages || data.messages.length === 0) {
                container.innerHTML = `<div class="no-chat-message">Nenhuma mensagem ainda</div>`;
                return;
            }

            data.messages.forEach(msg => {
                appendMessage(msg.sender.toLowerCase() === "user" ? "user" : "ai", msg.text);
            });

            container.scrollTop = container.scrollHeight;
        } catch (err) {
            console.error("Erro ao carregar mensagens:", err);
            container.innerHTML = `<div class="no-chat-message">Erro ao carregar mensagens.</div>`;
        }
    }

    // ========= NOVO CHAT =========
    const newChatBtn = document.getElementById("new-chat-btn");
    if (newChatBtn) {
        newChatBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            console.log("Botão Novo Chat clicado");

            try {
                const res = await fetch("/chat/new/", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                    },
                });

                if (!res.ok) {
                    const text = await res.text();
                    console.error("Erro ao criar chat:", res.status, text);
                    alert("Erro ao criar chat. Veja o console.");
                    return;
                }

                const data = await res.json(); // 🔹 Agora garantido que existe
                if (!data.chat_id || !data.title) {
                    console.error("Resposta inesperada:", data);
                    alert("Erro: resposta inesperada do servidor.");
                    return;
                }

                const chatList = document.querySelector(".chat-list");
                const li = document.createElement("li");
                li.classList.add("chat-item");
                li.dataset.chatId = data.chat_id;
                li.textContent = data.title;

                li.addEventListener("click", async () => {
                    document.querySelectorAll(".chat-item").forEach(i => i.classList.remove("active"));
                    li.classList.add("active");
                    currentChatId = li.dataset.chatId;
                    await loadChatMessages(currentChatId);
                });

                chatList.prepend(li);
                li.click(); // seleciona automaticamente

            } catch (err) {
                console.error("Erro ao criar novo chat:", err);
                alert("Erro de rede. Veja o console.");
            }
        });
    }

    // ========= ENVIAR MENSAGEM =========
    const sendBtn = document.getElementById("send-btn");
    if (sendBtn) {
        sendBtn.addEventListener("click", async () => {
            const input = document.getElementById("message-input");
            const mensagem = input.value.trim();
            if (!mensagem || !currentChatId) return;

            // ✅ Adiciona a mensagem do usuário imediatamente
            appendMessage("user", mensagem);
            input.value = "";

            try {
                const res = await fetch(`/processar_mensagem/${currentChatId}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: JSON.stringify({ mensagem }),
                });

                const data = await res.json();
                // Adiciona a resposta da IA
                appendMessage("ai", data.ai_message);

            } catch (err) {
                console.error("Erro ao enviar mensagem:", err);
                appendMessage("ai", "Erro ao enviar mensagem.");
            }
        });
    }

    // ========= GRAVAR ÁUDIO =========
    const recordBtn = document.getElementById("record-btn");
    if (recordBtn) {
        recordBtn.addEventListener("click", () => {
            if (!currentChatId) {
                alert("Selecione um chat primeiro!");
                return;
            }
            if (!mediaRecorder || mediaRecorder.state === "inactive") startRecording();
            else stopRecording();
        });
    }

    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                audioChunks = [];
                recordBtn.textContent = "🛑 Gravando...";

                mediaRecorder.addEventListener("dataavailable", e => audioChunks.push(e.data));
                mediaRecorder.addEventListener("stop", sendAudio);
            });
    }

    function stopRecording() {
        mediaRecorder.stop();
        recordBtn.textContent = "🎙️";
    }

    async function sendAudio() {
    const blob = new Blob(audioChunks, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio", blob, "recording.webm");

    try {
        const res = await fetch(`/processar_mensagem/${currentChatId}/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            body: formData,
        });

        if (!res.ok) {
            console.error("Erro HTTP ao enviar áudio:", res.status);
            appendMessage("ai", "⚠️ Erro ao processar áudio no servidor.");
            return;
        }

        let data;
        try {
            data = await res.json();
        } catch (parseErr) {
            console.error("Erro ao interpretar resposta JSON:", parseErr);
            appendMessage("ai", "⚠️ O servidor retornou uma resposta inválida.");
            return;
        }

        if (!data || !data.ai_message) {
            console.warn("Resposta inesperada do servidor:", data);
            appendMessage("ai", "⚠️ Nenhuma resposta da IA recebida.");
            return;
        }

        appendMessage("user", "(áudio enviado)");
        appendMessage("ai", data.ai_message);

    } catch (err) {
        console.error("Erro ao enviar áudio:", err);
        appendMessage("ai", "⚠️ Erro ao enviar o áudio. Veja o console.");
    } finally {
        recordBtn.textContent = "🎙️";
    }
}

    // ========= EXIBIR MENSAGENS =========
    function appendMessage(sender, text) {
        const container = document.getElementById("messages-container");
        const div = document.createElement("div");
        div.classList.add("message", sender);
        div.innerHTML = text;
        container.appendChild(div);

        // botão PDF abaixo da resposta da IA
        if (sender === "ai") {
            const btn = document.createElement("button");
            btn.textContent = "📄 Exportar para PDF";
            btn.classList.add("pdf-btn");
            btn.onclick = () => gerarPDF(currentChatId);

            const wrapper = document.createElement("div");
            wrapper.classList.add("pdf-btn-container");
            wrapper.appendChild(btn);
            container.appendChild(wrapper);
        }

        container.scrollTop = container.scrollHeight;
    }

    async function gerarPDF(chatId) {
        try {
            const res = await fetch(`/user_messages/gerar_pdf/${chatId}/`);
            if (!res.ok) throw new Error("Erro ao gerar PDF.");
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "documentacao_requisitos.pdf";
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Erro ao gerar PDF:", err);
            alert("Erro ao gerar PDF. Veja o console.");
        }
    }

    // ========= FUNÇÕES AUXILIARES =========
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    }

    function getCSRFToken() {
        const cookieMatch = document.cookie.split(";").map(c => c.trim()).find(c => c.startsWith("csrftoken="));
        if (cookieMatch) return decodeURIComponent(cookieMatch.split("=")[1]);
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute("content") : "";
    }
});





