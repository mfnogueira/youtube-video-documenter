# 📹 YouTube Video Documenter

Transforma vídeos do YouTube em documentação técnica estruturada em Markdown, com transcrição automática e análise inteligente por LLM.

## 🚀 Funcionalidades

1. **Download de vídeo** do YouTube (MP4)
2. **Extração de áudio** (MP3)
3. **Transcrição automática** usando OpenAI Whisper
   - Formato texto puro (`.txt`)
   - Formato legenda com timestamps (`.srt`)
   - Formato estruturado para LLMs (`.json`)
4. **Análise inteligente com LLM** 
   - Identifica momentos-chave do vídeo
   - Gera resumo estruturado em Markdown
   - Extrai frames apenas dos momentos importantes

## 📦 Instalação

### 1. Instalar dependências do sistema

```bash
# FFmpeg (necessário para yt-dlp)
sudo apt install ffmpeg

# Node.js (recomendado para yt-dlp)
sudo apt install nodejs
```

### 2. Instalar dependências Python

```bash
# Com uv (recomendado)
uv sync

# Ou com pip
pip install -r requirements.txt
```

### 3. Configurar API Key da OpenAI

1. Copie o arquivo de exemplo:
```bash
cp .env.example .env
```

2. Edite o arquivo `.env` e adicione sua chave:
```env
OPENAI_API_KEY=sk-proj-...
```

> 💡 Obtenha sua API key em: https://platform.openai.com/api-keys

## 🎯 Uso

### Passo 1: Processar o vídeo

```bash
uv run main.py
# Cole a URL do YouTube quando solicitado
```

**O que é gerado:**
- `conteudo_video/video.mp4` - Vídeo baixado
- `conteudo_video/video.mp3` - Áudio extraído
- `conteudo_video/transcricao.txt` - Transcrição em texto
- `conteudo_video/transcricao.srt` - Transcrição com timestamps (legenda)
- `conteudo_video/transcricao.json` - Transcrição estruturada

### Passo 2: Analisar com LLM e gerar resumo

```bash
uv run analisar_video.py
```

**O que é gerado:**
- `conteudo_video/analise.json` - Análise estruturada da LLM
- `conteudo_video/frames_importantes/` - Frames dos momentos-chave
- `conteudo_video/resumo.md` - **Resumo completo em Markdown**

## 📄 Exemplo de Saída (resumo.md)

```markdown
# Como Instalar Python no Windows

## Resumo Geral

Este vídeo apresenta um tutorial completo sobre como instalar...

---

## Introdução ao Python

**⏱️ Timestamp:** 0:00 - 2:30

![Frame em 0.0s](frames_importantes/frame_0.0s.jpg)

O vídeo começa explicando o que é Python e suas aplicações...

> *"Python é uma das linguagens mais populares do mundo"*

---

## Download e Instalação

**⏱️ Timestamp:** 2:30 - 8:45

![Frame em 300.0s](frames_importantes/frame_300.0s.jpg)

Passo a passo detalhado do processo de instalação...
```

## 🔧 Configuração Avançada

### Mudar modelo Whisper

Edite `main.py`, linha 28:

```python
model = whisper.load_model("base")  # Opções: tiny, base, small, medium, large
```

### Mudar modelo GPT

Edite `analisar_video.py`, linha 58:

```python
model="gpt-4o-mini"  # Ou: gpt-4o, gpt-4-turbo
```

## 💰 Custos

- **Whisper (local):** Gratuito
- **GPT-4o-mini:** ~$0.001 por vídeo de 1 hora (~$0.15/1M tokens)

## 📁 Estrutura do Projeto

```
youtube-video-documenter/
├── main.py                  # Processamento principal
├── analisar_video.py        # Análise com LLM
├── .env                     # Chaves de API (não commitado)
├── .env.example             # Exemplo de configuração
├── pyproject.toml           # Dependências
└── conteudo_video/          # Saída (não commitado)
    ├── video.mp4
    ├── video.mp3
    ├── transcricao.txt
    ├── transcricao.srt
    ├── transcricao.json
    ├── analise.json
    ├── resumo.md
    └── frames_importantes/
        ├── frame_0.0s.jpg
        ├── frame_150.5s.jpg
        └── ...
```

## 🤝 Contribuindo

Sinta-se à vontade para abrir issues ou pull requests!

## 📝 Licença

MIT
