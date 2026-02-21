import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from main import extrair_frames_por_timestamps

# Carrega variáveis de ambiente
load_dotenv()

def analisar_transcricao_com_llm(transcricao_json_path, pasta_saida='conteudo_video'):
    """
    Analisa a transcrição usando GPT-4o-mini e gera um resumo em markdown.

    Args:
        transcricao_json_path: Caminho para o arquivo transcricao.json
        pasta_saida: Pasta onde está o vídeo e onde salvar os frames
    """
    # Verifica se a API key está configurada
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ ERRO: OPENAI_API_KEY não encontrada no arquivo .env")
        return

    # Carrega a transcrição
    print("📖 Carregando transcrição...")
    with open(transcricao_json_path, 'r', encoding='utf-8') as f:
        transcricao = json.load(f)

    # Prepara o prompt para a LLM
    prompt = f"""Analise a seguinte transcrição de um vídeo técnico/tutorial e extraia APENAS o conteúdo técnico relevante.

TRANSCRIÇÃO COMPLETA:
{transcricao['texto_completo']}

SEGMENTOS COM TIMESTAMPS:
{json.dumps(transcricao['segmentos'], ensure_ascii=False, indent=2)}

INSTRUÇÕES CRÍTICAS:

1. IGNORE COMPLETAMENTE:
   ❌ Apresentações pessoais ("Meu nome é...", "Sou supervisor...")
   ❌ Saudações e boas-vindas
   ❌ Agradecimentos e despedidas
   ❌ Introduções genéricas
   ❌ Qualquer conteúdo que não seja técnico/prático

2. FOQUE EXCLUSIVAMENTE EM:
   ✅ Demonstrações práticas de software/ferramentas
   ✅ Configurações sendo aplicadas
   ✅ Técnicas sendo ensinadas
   ✅ Exemplos de código ou implementação
   ✅ Dashboards, gráficos ou visualizações sendo criados
   ✅ Processos técnicos sendo executados
   ✅ Boas práticas e dicas técnicas
   ✅ Troubleshooting e resolução de problemas

3. O RESUMO DEVE SER:
   - Uma documentação técnica, NÃO uma narrativa do vídeo
   - Focado em "O QUE" foi ensinado, NÃO em "QUEM" ensinou
   - Útil para alguém que quer aprender a técnica, sem contexto social

4. TIMESTAMPS:
   - Identifique 10-20 momentos técnicos
   - Escolha timestamps onde TELAS/INTERFACES estão visíveis
   - Palavras-chave: "vou mostrar", "aqui você", "essa tela", "configurar", "criar", "ajustar"

5. CADA SEÇÃO deve descrever:
   - A técnica/ferramenta/conceito sendo demonstrado
   - Passos práticos sendo executados
   - O que está visível na tela naquele momento

Retorne um JSON no seguinte formato:
{{
  "titulo": "Título técnico do conteúdo (ex: 'Construção de Dashboards em HTML5')",
  "resumo_geral": "Resumo TÉCNICO: quais ferramentas, técnicas e conceitos são abordados. Liste os tópicos principais de forma objetiva.",
  "secoes": [
    {{
      "titulo": "Nome da técnica/ferramenta/conceito (ex: 'Configuração de Gráficos Dinâmicos')",
      "timestamp_inicio": 0.0,
      "timestamp_fim": 120.5,
      "timestamp_frame": 60.0,
      "tipo_conteudo": "tela_software|configuracao|dashboard|codigo|diagrama|exemplo_pratico|boas_praticas",
      "descricao": "Explicação TÉCNICA: o que está sendo feito, quais passos, que resultado é obtido",
      "citacao": "Frase técnica relevante (apenas se for uma dica/conceito importante)"
    }}
  ],
  "conclusao": "Principais técnicas e conceitos abordados - lista objetiva"
}}

IMPORTANTE: Retorne APENAS o JSON, sem texto adicional antes ou depois.
"""

    # Chama a API da OpenAI
    print("🤖 Analisando com GPT-4o-mini...")
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um assistente especializado em analisar e resumir conteúdo de vídeos. Retorne sempre JSON válido."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    # Parse da resposta
    analise = json.loads(response.choices[0].message.content)

    # Salva a análise em JSON
    analise_path = f'{pasta_saida}/analise.json'
    with open(analise_path, 'w', encoding='utf-8') as f:
        json.dump(analise, f, ensure_ascii=False, indent=2)
    print(f"✓ Análise salva: {analise_path}")

    # Extrai frames dos momentos-chave
    print("\n📸 Extraindo frames dos momentos-chave...")
    video_path = None
    for ext in ['.mp4', '.webm', '.mkv']:
        possible_path = f'{pasta_saida}/video{ext}'
        if os.path.exists(possible_path):
            video_path = possible_path
            break

    if not video_path:
        print("❌ Vídeo não encontrado!")
        return analise

    timestamps = [secao['timestamp_frame'] for secao in analise['secoes']]
    frames_dir = f'{pasta_saida}/frames_importantes'
    extrair_frames_por_timestamps(video_path, timestamps, frames_dir)

    # Gera o markdown
    print("\n📝 Gerando resumo em Markdown...")
    markdown = gerar_markdown(analise, frames_dir)

    markdown_path = f'{pasta_saida}/resumo.md'
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✓ Resumo salvo: {markdown_path}")
    print(f"\n✅ Processo concluído!")

    return analise

def gerar_markdown(analise, frames_dir):
    """Gera o markdown estruturado com imagens dos frames"""

    md = f"# {analise['titulo']}\n\n"
    md += "## 📋 Visão Técnica\n\n"
    md += f"{analise['resumo_geral']}\n\n"
    md += "---\n\n"
    md += "## 🔧 Conteúdo Técnico\n\n"

    for i, secao in enumerate(analise['secoes']):
        # Título da seção
        md += f"### {i+1}. {secao['titulo']}\n\n"

        # Tipo de conteúdo e timestamp
        tipo_emoji = {
            'tela_software': '💻',
            'configuracao': '⚙️',
            'dashboard': '📊',
            'codigo': '👨‍💻',
            'diagrama': '📈',
            'exemplo_pratico': '🎯',
            'boas_praticas': '✨'
        }
        tipo = secao.get('tipo_conteudo', 'exemplo_pratico')
        emoji = tipo_emoji.get(tipo, '📌')

        timestamp_inicio = int(secao['timestamp_inicio'])
        timestamp_fim = int(secao['timestamp_fim'])
        md += f"{emoji} **Tipo:** {tipo.replace('_', ' ').title()} | "
        md += f"**⏱️ Timestamp:** {timestamp_inicio // 60}:{timestamp_inicio % 60:02d} - {timestamp_fim // 60}:{timestamp_fim % 60:02d}\n\n"

        # Frame
        frame_filename = f"frame_{secao['timestamp_frame']:.1f}s.jpg"
        md += f"![Frame em {secao['timestamp_frame']:.1f}s]({frames_dir}/{frame_filename})\n\n"

        # Descrição
        md += f"{secao['descricao']}\n\n"

        # Citação (se houver)
        if secao.get('citacao'):
            md += f"> 💬 *\"{secao['citacao']}\"*\n\n"

        md += "\n"

    # Conclusão
    md += "---\n\n"
    md += "## 💡 Resumo dos Conceitos Principais\n\n"
    md += f"{analise['conclusao']}\n"

    return md

# --- Execução ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        pasta = sys.argv[1]
    else:
        pasta = 'conteudo_video'

    transcricao_path = f'{pasta}/transcricao.json'

    if not os.path.exists(transcricao_path):
        print(f"❌ Arquivo não encontrado: {transcricao_path}")
        print("Execute primeiro o main.py para processar um vídeo.")
        sys.exit(1)

    analisar_transcricao_com_llm(transcricao_path, pasta)
