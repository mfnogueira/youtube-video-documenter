import os
import cv2
import yt_dlp
import whisper
import json

def format_timestamp(seconds):
    """Converte segundos para formato SRT (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def extrair_frames_por_timestamps(video_path, timestamps, pasta_saida='frames'):
    """
    Extrai frames do vídeo em timestamps específicos.

    Args:
        video_path: Caminho para o arquivo de vídeo
        timestamps: Lista de segundos onde extrair frames (ex: [10.5, 25.3, 120.0])
        pasta_saida: Pasta onde salvar os frames
    """
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERRO: Não foi possível abrir o vídeo {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"\nExtraindo {len(timestamps)} frames específicos...")

    for i, timestamp in enumerate(timestamps):
        frame_number = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        ret, frame = cap.read()
        if ret:
            filename = f"{pasta_saida}/frame_{timestamp:.1f}s.jpg"
            cv2.imwrite(filename, frame)
            print(f"✓ Frame extraído em {timestamp:.1f}s: {filename}")
        else:
            print(f"✗ Erro ao extrair frame em {timestamp:.1f}s")

    cap.release()
    print(f"Processo concluído. {len(timestamps)} frames extraídos.")

def processar_youtube(url, pasta_saida='conteudo_video', extrair_todos_frames=False):
    # Cria a pasta de saída se não existir
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # 1. Download do vídeo e extração de áudio
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{pasta_saida}/video.%(ext)s',
        'keepvideo': True,  # Mantém o vídeo após extrair o áudio
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    print("Baixando vídeo e convertendo áudio...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    # Detecta o arquivo de vídeo baixado
    video_files = [f for f in os.listdir(pasta_saida) if f.startswith('video.') and f.endswith(('.mp4', '.webm', '.mkv'))]

    if not video_files:
        print("ERRO: Nenhum arquivo de vídeo foi baixado!")
        return

    video_path = os.path.join(pasta_saida, video_files[0])
    audio_path = f'{pasta_saida}/video.mp3'

    print(f"Vídeo baixado: {video_path}")
    print(f"Áudio salvo: {audio_path}")

    # 2. Transcrição do áudio usando Whisper
    print("\nIniciando transcrição do áudio...")
    print("Carregando modelo Whisper (pode demorar na primeira vez)...")

    # Usando modelo 'base' - balanceado entre velocidade e precisão
    # Opções: tiny, base, small, medium, large
    model = whisper.load_model("base")

    print("Transcrevendo áudio (isso pode levar alguns minutos)...")
    result = model.transcribe(audio_path, language="pt", verbose=False)

    # Salva a transcrição completa (sem timestamps)
    transcricao_txt = f'{pasta_saida}/transcricao.txt'
    with open(transcricao_txt, 'w', encoding='utf-8') as f:
        f.write(result["text"])

    # Salva a transcrição com timestamps (formato SRT - legenda)
    transcricao_srt = f'{pasta_saida}/transcricao.srt'
    with open(transcricao_srt, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result["segments"], start=1):
            # Formato SRT: número, timestamp, texto
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{segment['text'].strip()}\n\n")

    # Salva também em JSON para fácil processamento por LLM
    transcricao_json = f'{pasta_saida}/transcricao.json'
    with open(transcricao_json, 'w', encoding='utf-8') as f:
        json.dump({
            'texto_completo': result["text"],
            'segmentos': [
                {
                    'inicio': seg["start"],
                    'fim': seg["end"],
                    'texto': seg["text"].strip()
                }
                for seg in result["segments"]
            ]
        }, f, ensure_ascii=False, indent=2)

    print(f"✓ Transcrição texto: {transcricao_txt}")
    print(f"✓ Transcrição SRT (com timestamps): {transcricao_srt}")
    print(f"✓ Transcrição JSON: {transcricao_json}")
    print(f"Prévia: {result['text'][:200]}...")

    # 3. Captura de Frames (Opcional)
    if extrair_todos_frames:
        print("\n⚠️  Extraindo TODOS os frames (a cada 5s) - pode gerar muitos arquivos!")
        print("Dica: Use a função extrair_frames_por_timestamps() com timestamps da LLM")

        # Verifica se o arquivo de vídeo existe
        if not os.path.exists(video_path):
            print(f"ERRO: Vídeo não encontrado em {video_path}")
            return

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"ERRO: Não foi possível abrir o vídeo {video_path}")
            return

        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"FPS do vídeo: {frame_rate}")
        print(f"Total de frames: {total_frames}")

        intervalo_segundos = 5
        frame_interval = int(frame_rate * intervalo_segundos)

        print(f"Capturando 1 frame a cada {intervalo_segundos} segundos")

        count = 0
        saved_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if count % frame_interval == 0:
                filename = f"{pasta_saida}/frame_{saved_count:04d}.jpg"
                cv2.imwrite(filename, frame)
                saved_count += 1

            count += 1

        cap.release()
        print(f"✓ {saved_count} frames salvos em '{pasta_saida}'")
    else:
        print("\n📌 Frames não foram extraídos automaticamente.")
        print("   Workflow recomendado:")
        print("   1. Analise a transcrição com uma LLM")
        print("   2. Identifique os timestamps importantes")
        print("   3. Use extrair_frames_por_timestamps() para capturar apenas esses momentos")

    print(f"\n✅ Processamento concluído!")
    print(f"   📁 Pasta de saída: {pasta_saida}")
    return video_path

# --- Execução ---
if __name__ == "__main__":
    url_video = input("Cole a URL do YouTube: ")

    # Processa o vídeo (sem extrair todos os frames)
    video_path = processar_youtube(url_video, extrair_todos_frames=False)

    # Exemplo: extrair frames em momentos específicos (após análise da LLM)
    # timestamps_importantes = [15.5, 45.2, 120.8, 300.0]  # segundos
    # extrair_frames_por_timestamps(video_path, timestamps_importantes, 'conteudo_video/frames_importantes')
