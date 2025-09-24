# Projeto RequisitosAI

Bem-vindo ao **RequisitosAI**, um projeto que gera **requisitos funcionais, não funcionais, histórias de usuário e critérios de aceitação** a partir de áudio ou texto de reuniões, utilizando:

- **Whisper**: para transcrição de áudio.
- **Gemini API**: para análise e geração de requisitos estruturados.

---

## ⚙️ Configuração do Ambiente

### 1. Clone o repositório

```bash
git clone https://github.com/brun0m/Extensao-3.git
cd Extensao-3
```

### 2. Crie e ative um ambiente virtual

Windows:
```
python -m venv .venv
.venv\Scripts\Activate
```

Linux / Mac:
```
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências
```
pip install -r requirements.txt
```

### 4. Configure a chave da Gemini API

O Gemini SDK pode ler a chave de duas maneiras:

I) Variável de ambiente do sistema

No Windows(cmd ou PowerShell):
```
setx GEMINI_API_KEY "sua_chave_aqui"
```

No Linux/Mac:
```
export GEMINI_API_KEY="sua_chave_aqui"
```

II) Através do arquivo .env

Crie um arquivo chamado .env na raiz do projeto e escreva:
```
GEMINI_API_KEY=sua_chave_aqui
```

E no Python, use python-dotenv para carregar:
```
from dotenv import load_dotenv
import os

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
```

### 5. Configuração do Whisper

O Whisper precisa do PATH correto do ffmpeg no seu sistema para processar áudio.

Windows: adicione o diretório da pasta bin à variável de ambiente PATH. -> https://www.gyan.dev/ffmpeg/builds/ (Escolha a versão Release Full ou uma mais recente)

Linux/Mac: instale via pacote do sistema (sudo apt install ffmpeg ou brew install ffmpeg)

Você pode testar se está configurado:
```
ffmpeg -version
```
Se aparecer a versão, o Whisper vai funcionar corretamente.

### Executando o Projeto:

I) Rode o servidor Django:
```
python manage.py runserver
```
II) Abra no navegador:
```
http://127.0.0.1:8000/
```
III) Use o botão de gravação para enviar áudios ou digite o texto da reunião.
O sistema retorna os requisitos, histórias de usuário e critérios de aceitação.



