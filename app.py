import base64

import streamlit as st
import pandas as pd

# ============================================================
# INCLUSÃO COMPARTILHADA
# Painel de atividades pedagógicas inclusivas, alimentado por
# Google Forms + Google Planilhas.
# ============================================================

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Inclusão Compartilhada",
    page_icon="🧩",
    layout="wide",
    # Em telas estreitas (celular), o Streamlit normalmente esconde o menu
    # lateral e mostra apenas uma pequena setinha "»" no canto superior
    # esquerdo para abri-lo. Em alguns navegadores embutidos (como o do
    # WhatsApp), essa setinha fica pouco visível/pouco perceptível, dando a
    # impressão de que as abas "Estatísticas do Projeto" e "Avaliar
    # Plataforma" sumiram. Começar com o menu já aberto ("expanded") garante
    # que a navegação apareça de cara também no celular.
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# 2.1 AJUSTES DE CSS PARA CELULAR
#
# - Aumenta e destaca a setinha de abrir/fechar o menu lateral
#   (por padrão ela é pequena e cinza-clara, quase invisível em telas
#   pequenas ou em navegadores embutidos de apps como o WhatsApp).
# - Evita que o rodapé/menu "Manage app" do Streamlit Cloud (visível
#   apenas para quem está logado na conta do Streamlit, com foto de
#   perfil e botão colorido) sobreponha o conteúdo da página para quem
#   está apenas visitando o link público.
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Setinha de abrir o menu lateral quando ele está fechado */
    [data-testid="collapsedControl"] {
        background-color: #4F6F52 !important;
        border-radius: 8px !important;
        padding: 6px !important;
        opacity: 1 !important;
        visibility: visible !important;
        z-index: 999999 !important;
    }
    [data-testid="collapsedControl"] svg {
        color: white !important;
        fill: white !important;
        width: 1.6rem !important;
        height: 1.6rem !important;
    }
    /* Evita que a barra/rodapé "Manage app" do Streamlit Cloud (só
       aparece para quem está logado na conta dona do app) cubra o
       conteúdo em telas pequenas. */
    @media (max-width: 640px) {
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"] {
            z-index: 1 !important;
        }
        .main .block-container {
            padding-bottom: 4rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 2. MODO DE TESTE
#
# Enquanto o Formulário e a Planilha reais não estiverem prontos
# (ou enquanto você estiver testando/apresentando o projeto),
# deixe MODO_TESTE = True: o app usa dados de exemplo embutidos
# no próprio código, então funciona mesmo sem internet ou sem os
# links do Google configurados.
#
# Quando o Formulário de cadastro e a planilha de respostas
# estiverem publicados (ver README.md, seção "Como configurar"),
# preencha as URLs abaixo e mude para MODO_TESTE = False.
# ------------------------------------------------------------
MODO_TESTE = False

# URLs reais dos formulários e planilhas do Google.
URL_RESPOSTAS_ATIVIDADES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRjw5AMHEDN0c6o8oczs0btovR0nJyuUyOveNtuydaBYUMr0ztSa3yu1RDNlHmDHsYXn9Q2EnzbVvM1/pub?output=csv"
LINK_GOOGLE_FORMS_CADASTRO = "https://docs.google.com/forms/d/e/1FAIpQLSdB7NQtkg3IP7s314YFxc1mJ5AgPi-vSHsxXvNBqQSNFB5geA/viewform"
LINK_GOOGLE_FORMS_AVALICAO = "https://docs.google.com/forms/d/e/1FAIpQLSdRMuq-Yzw8-voPG1iJVPb8xfwOaX0KjbkzCd1GbbANlq253w/viewform"
URL_RESPOSTAS_AVALIACOES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNHeeC29SuqocCf1MWM9WciTJU_pKGZIP4l07GBM178_KVisUlz9oRpTA_0E-SzQfW2XBSCEK3DMyv/pub?output=csv"

_PLACEHOLDER_EXATOS = ("https://google.com", "http://google.com", "google.com")
_PLACEHOLDER_MARKERS = ("PLACEHOLDER", "SUA_PLANILHA", "SUA_SUA")


def _eh_placeholder(url: str) -> bool:
    """Detecta se uma URL/link ainda não foi configurado pelo usuário.

    Compara com igualdade exata contra o placeholder padrão ("google.com"),
    em vez de checar substring — caso contrário, links reais e válidos do
    Google Forms/Planilhas (que também contêm "google.com") seriam
    incorretamente tratados como não configurados.
    """
    if not url:
        return True
    if url.strip().rstrip("/") in _PLACEHOLDER_EXATOS:
        return True
    return any(marcador in url for marcador in _PLACEHOLDER_MARKERS)


# 3. DADOS DE EXEMPLO (usados no Modo de Teste e como rede de segurança
#    caso a planilha real ainda não tenha respostas)
#
#    Cobrem os 8 tipos de deficiência/neurodivergência do formulário, cada um
#    com 1 atividade, 1 artigo e 1 exercício didático, para que a plataforma já
#    tenha exemplos de uso reais assim que publicada — mesmo antes da
#    comunidade enviar suas próprias contribuições.
_COL_TITULO_REAL = "Título da atividade"
_COL_DEF_REAL = "Para qual tipo de deficiência ou neurodivergência esta atividade foi pensada?"
_COL_TIPO_CONTEUDO = "Tipo de Conteúdo"
_COL_ILUSTRACAO = "Ilustração"


# ------------------------------------------------------------
# 3.1 ILUSTRAÇÕES DE CADA CATEGORIA (SVG embutido, sem arquivos externos)
#
# Seguindo a mesma lógica de "baixa manutenção e risco jurídico quase
# zero" do restante do projeto (ver Plano_Inicial_Conversa_com_IA.md):
# em vez de hospedar imagens externas (que podem sair do ar, mudar de
# licença ou pesar no carregamento), cada categoria tem um pequeno
# ícone/ilustração vetorial (SVG) desenhado especificamente para este
# projeto e embutido diretamente no código como "data URI". Isso
# garante que a ilustração sempre aparece, mesmo offline, sem depender
# de nenhum serviço externo.
# ------------------------------------------------------------
def _svg_para_data_uri(svg: str) -> str:
    codificado = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{codificado}"


_SVG_TEA = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="95" fill="#EAF2FB"/>
  <path d="M60 100c0-16 13-29 29-29 12 0 20 7 31 18 11-11 19-18 31-18 16 0 29 13 29 29s-13 29-29 29c-12 0-20-7-31-18-11 11-19 18-31 18-16 0-29-13-29-29z"
        fill="none" stroke="#4F6F52" stroke-width="12" stroke-linecap="round"/>
  <path d="M60 100c0-16 13-29 29-29 12 0 20 7 31 18" fill="none" stroke="#F5A623" stroke-width="6" stroke-linecap="round"/>
  <path d="M120 89c11-11 19-18 31-18 16 0 29 13 29 29" fill="none" stroke="#7ED6A5" stroke-width="6" stroke-linecap="round"/>
</svg>
"""

_SVG_TDAH = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="95" fill="#FFF3E0"/>
  <path d="M100 42c-24 0-40 17-40 36 0 7 2 13 4 16-11 5-18 15-18 26 0 15 12 27 27 27h2c3 12 14 20 27 20 10 0 18-4 24-11 5 4 12 6 18 6 16 0 28-13 28-28 0-9-4-17-11-23 4-6 6-13 6-20 0-21-18-38-40-38-9 0-18 3-25 9-1-9-1-20-2-20z"
        fill="#4F6F52" fill-opacity="0.15" stroke="#4F6F52" stroke-width="6"/>
  <polygon points="108,55 82,112 100,112 90,150 130,93 106,93" fill="#F5A623"/>
</svg>
"""

_SVG_AUDITIVA = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="95" fill="#E8F7EE"/>
  <path d="M78 152c-17 0-30-14-30-31V92c0-6 5-11 11-11s11 5 11 11v18"
        fill="none" stroke="#4F6F52" stroke-width="10" stroke-linecap="round"/>
  <rect x="66" y="56" width="16" height="56" rx="8" fill="#4F6F52"/>
  <rect x="89" y="50" width="16" height="62" rx="8" fill="#4F6F52"/>
  <rect x="112" y="56" width="16" height="56" rx="8" fill="#4F6F52"/>
  <path d="M140 82c11 8 11 32 0 40" fill="none" stroke="#7ED6A5" stroke-width="6" stroke-linecap="round"/>
  <path d="M153 70c19 14 19 48 0 62" fill="none" stroke="#7ED6A5" stroke-width="6" stroke-linecap="round"/>
</svg>
"""

_SVG_VISUAL = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="95" fill="#EFF3FB"/>
  <path d="M28 100c20-30 50-46 72-46s52 16 72 46c-20 30-50 46-72 46s-52-16-72-46z"
        fill="none" stroke="#4F6F52" stroke-width="8"/>
  <circle cx="100" cy="100" r="24" fill="#4F6F52"/>
  <circle cx="92" cy="92" r="6" fill="#FFFFFF"/>
  <g fill="#F5A623">
    <circle cx="55" cy="152" r="5"/>
    <circle cx="70" cy="152" r="5"/>
    <circle cx="55" cy="166" r="5"/>
    <circle cx="130" cy="152" r="5"/>
    <circle cx="145" cy="152" r="5"/>
    <circle cx="130" cy="166" r="5"/>
  </g>
</svg>
"""

_SVG_FISICA = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="95" fill="#EAF2FB"/>
  <circle cx="112" cy="55" r="14" fill="#4F6F52"/>
  <path d="M100 80l10 30h30a8 8 0 010 16h-24l18 34a8 8 0 01-14 8l-22-40-12 10a10 10 0 01-13-15l20-17 3-26z"
        fill="#4F6F52"/>
  <circle cx="95" cy="140" r="38" fill="none" stroke="#F5A623" stroke-width="8"/>
  <line x1="95" y1="140" x2="120" y2="120" stroke="#F5A623" stroke-width="6" stroke-linecap="round"/>
</svg>
"""

_SVG_INTELECTUAL_DOWN = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="95" fill="#FDEEF3"/>
  <path d="M100 145s-42-26-42-58c0-17 14-29 29-29 8 0 16 4 13 12 3-8 21-12 29 0 0 0 13 12 13 29 0 32-42 58-42 58z"
        fill="#E0567C"/>
  <path d="M45 152c10-14 26-22 30-8 4-12 22-18 34-6" fill="none" stroke="#4F6F52" stroke-width="8" stroke-linecap="round"/>
  <path d="M155 152c-10-14-26-22-30-8-4-12-22-18-34-6" fill="none" stroke="#4F6F52" stroke-width="8" stroke-linecap="round"/>
</svg>
"""

_SVG_DISLEXIA_DISCALCULIA = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="95" fill="#F5F0FA"/>
  <path d="M100 60c-14-10-38-14-56-8v78c18-6 42-2 56 8 14-10 38-14 56-8V52c-18-6-42-2-56 8z"
        fill="#4F6F52" fill-opacity="0.15" stroke="#4F6F52" stroke-width="6"/>
  <line x1="100" y1="60" x2="100" y2="138" stroke="#4F6F52" stroke-width="6"/>
  <text x="58" y="98" font-family="Arial, sans-serif" font-size="24" fill="#F5A623" font-weight="bold">b</text>
  <text x="118" y="98" font-family="Arial, sans-serif" font-size="24" fill="#7ED6A5" font-weight="bold">d</text>
  <text x="58" y="128" font-family="Arial, sans-serif" font-size="22" fill="#E0567C" font-weight="bold">3</text>
  <text x="118" y="128" font-family="Arial, sans-serif" font-size="22" fill="#4F6F52" font-weight="bold">8</text>
</svg>
"""

_SVG_MULTIPLAS = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="95" fill="#EAF6F4"/>
  <path d="M40 95a60 60 0 01120 0z" fill="#4F6F52"/>
  <path d="M40 95a60 60 0 0130-52 60 60 0 0130 52z" fill="#F5A623"/>
  <path d="M100 43a60 60 0 0130 52 60 60 0 01-30-52z" fill="#7ED6A5"/>
  <line x1="100" y1="95" x2="100" y2="150" stroke="#5A5A5A" stroke-width="6" stroke-linecap="round"/>
  <path d="M100 150c0 8 8 12 14 6" fill="none" stroke="#5A5A5A" stroke-width="6" stroke-linecap="round"/>
  <circle cx="70" cy="165" r="10" fill="#E0567C"/>
  <circle cx="100" cy="172" r="10" fill="#4F6F52"/>
  <circle cx="130" cy="165" r="10" fill="#7ED6A5"/>
</svg>
"""

_SVG_ILUSTRACOES = {
    "TEA (Transtorno do Espectro Autista)": _svg_para_data_uri(_SVG_TEA),
    "TDAH": _svg_para_data_uri(_SVG_TDAH),
    "Deficiência Auditiva": _svg_para_data_uri(_SVG_AUDITIVA),
    "Deficiência Visual": _svg_para_data_uri(_SVG_VISUAL),
    "Deficiência Física/Motora": _svg_para_data_uri(_SVG_FISICA),
    "Deficiência Intelectual / Síndrome de Down": _svg_para_data_uri(_SVG_INTELECTUAL_DOWN),
    "Dislexia / Discalculia": _svg_para_data_uri(_SVG_DISLEXIA_DISCALCULIA),
    "Múltiplas deficiências / Outro": _svg_para_data_uri(_SVG_MULTIPLAS),
}

DADOS_EXEMPLO_ATIVIDADES = pd.DataFrame([
    # --- TEA (Transtorno do Espectro Autista) ---
    {
        _COL_TITULO_REAL: "Caça ao tesouro sensorial",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Circuito com texturas, sons e cheiros variados para exploração sensorial guiada, com rotina visual antecipando cada estação.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "1º ano",
        _COL_DEF_REAL: "TEA (Transtorno do Espectro Autista)",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Rotinas visuais em sala de aula: um apoio simples para a autonomia de alunos autistas",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo para educadores explicando o que são rotinas visuais, por que reduzem a ansiedade em momentos de transição e como montar uma com poucos recursos (cartões, pictogramas, quadro de rotina do dia).",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "1º ano",
        _COL_DEF_REAL: "TEA (Transtorno do Espectro Autista)",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Monte sua rotina visual do dia",
        _COL_TIPO_CONTEUDO: "Exercício Didático",
        "Descrição da Atividade": "Exercício de sequenciamento: o aluno organiza cartões de atividades (chegada, roda de leitura, lanche, recreio, saída) na ordem correta, fixando-os em um quadro de rotina.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "1º ano",
        _COL_DEF_REAL: "TEA (Transtorno do Espectro Autista)",
        "Link do Vídeo/Conteúdo": "",
    },
    # --- TDAH ---
    {
        _COL_TITULO_REAL: "Corrida dos números com pausas ativas",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Atividade de matemática com deslocamento físico entre estações, pensada para manter o foco e permitir gasto de energia.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "4º ano",
        _COL_DEF_REAL: "TDAH",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Pausas ativas em sala de aula: por que funcionam para alunos com TDAH",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo explicando a relação entre movimento e atenção, com sugestões práticas de pausas de 2 a 5 minutos para intercalar entre blocos de atividade.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "4º ano",
        _COL_DEF_REAL: "TDAH",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Semáforo da autorregulação",
        _COL_TIPO_CONTEUDO: "Exercício Didático",
        "Descrição da Atividade": "Ficha com três cores (verde, amarelo, vermelho) para o aluno sinalizar seu nível de agitação/foco ao longo da aula, treinando autopercepção.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "4º ano",
        _COL_DEF_REAL: "TDAH",
        "Link do Vídeo/Conteúdo": "",
    },
    # --- Deficiência Auditiva ---
    {
        _COL_TITULO_REAL: "Contação de histórias em Libras",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "História narrada em Libras com apoio de imagens e legenda simultânea em português.",
        "Idade Recomendada": "3-5 anos",
        "Série Escolar": "Educação Infantil",
        _COL_DEF_REAL: "Deficiência Auditiva",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Libras na sala de aula comum: primeiros passos para professores ouvintes",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com sinais básicos de acolhimento em Libras e orientações para criar um ambiente visualmente acessível para alunos surdos.",
        "Idade Recomendada": "3-5 anos",
        "Série Escolar": "Educação Infantil",
        _COL_DEF_REAL: "Deficiência Auditiva",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Jogo da memória com o alfabeto manual",
        _COL_TIPO_CONTEUDO: "Exercício Didático",
        "Descrição da Atividade": "Jogo de cartas que pareia cada letra do alfabeto com sua configuração correspondente em Libras, reforçando o reconhecimento do alfabeto manual.",
        "Idade Recomendada": "3-5 anos",
        "Série Escolar": "Educação Infantil",
        _COL_DEF_REAL: "Deficiência Auditiva",
        "Link do Vídeo/Conteúdo": "",
    },
    # --- Deficiência Visual ---
    {
        _COL_TITULO_REAL: "Mapa tátil do bairro",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Maquete tátil com texturas diferentes representando ruas, praças e pontos de referência do entorno da escola.",
        "Idade Recomendada": "12-14 anos",
        "Série Escolar": "7º ano",
        _COL_DEF_REAL: "Deficiência Visual",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Descrevendo imagens e criando materiais táteis: acessibilidade na prática",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com técnicas de descrição de imagem para alunos com baixa visão ou cegueira e dicas de materiais de baixo custo para criar texturas em relevo.",
        "Idade Recomendada": "12-14 anos",
        "Série Escolar": "7º ano",
        _COL_DEF_REAL: "Deficiência Visual",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Reconhecimento de texturas",
        _COL_TIPO_CONTEUDO: "Exercício Didático",
        "Descrição da Atividade": "Caça a objetos por toque: o aluno identifica formas geométricas e texturas guardadas em uma caixa sensorial, descrevendo em voz alta o que sente.",
        "Idade Recomendada": "12-14 anos",
        "Série Escolar": "7º ano",
        _COL_DEF_REAL: "Deficiência Visual",
        "Link do Vídeo/Conteúdo": "",
    },
    # --- Deficiência Física/Motora ---
    {
        _COL_TITULO_REAL: "Boliche adaptado",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Jogo de boliche com pinos leves e rampa de lançamento, permitindo participação de alunos com diferentes níveis de mobilidade de mãos e braços.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "Deficiência Física/Motora",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Adaptando materiais escolares para alunos com deficiência física",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com exemplos de adaptações simples e de baixo custo — engrossadores de lápis, apoios de mesa, pranchas inclinadas — para tarefas do dia a dia em sala.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "Deficiência Física/Motora",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Circuito de coordenação com apoio",
        _COL_TIPO_CONTEUDO: "Exercício Didático",
        "Descrição da Atividade": "Percurso curto com pegadores adaptados e superfícies variadas, trabalhando coordenação motora no ritmo de cada aluno.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "Deficiência Física/Motora",
        "Link do Vídeo/Conteúdo": "",
    },
    # --- Deficiência Intelectual / Síndrome de Down ---
    {
        _COL_TITULO_REAL: "Comunicação alternativa no recreio",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Cartões de Comunicação Alternativa (CAA) plastificados para mediar brincadeiras coletivas no intervalo.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "Deficiência Intelectual / Síndrome de Down",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Comunicação Alternativa e Aumentativa (CAA): guia rápido para o dia a dia escolar",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo introdutório sobre CAA, com exemplos de pranchas de comunicação simples para pedidos, sentimentos e escolhas do dia a dia.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "Deficiência Intelectual / Síndrome de Down",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Sequência de rotina com cartões de CAA",
        _COL_TIPO_CONTEUDO: "Exercício Didático",
        "Descrição da Atividade": "O aluno organiza cartões de CAA na ordem correta das etapas de uma tarefa simples (por exemplo, lavar as mãos), reforçando a compreensão sequencial.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "Deficiência Intelectual / Síndrome de Down",
        "Link do Vídeo/Conteúdo": "",
    },
    # --- Dislexia / Discalculia ---
    {
        _COL_TITULO_REAL: "Leitura compartilhada com apoio de áudio",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Leitura em dupla de um texto curto com faixa de áudio sincronizada e fonte ampliada e espaçada, reduzindo a carga de decodificação do texto.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "5º ano",
        _COL_DEF_REAL: "Dislexia / Discalculia",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Fonte, espaçamento e cor: pequenas mudanças que ajudam alunos com dislexia",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com orientações práticas de formatação de material impresso e digital (tipo de fonte, espaçamento entre linhas, contraste) para alunos com dislexia.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "5º ano",
        _COL_DEF_REAL: "Dislexia / Discalculia",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Reta numérica manipulável",
        _COL_TIPO_CONTEUDO: "Exercício Didático",
        "Descrição da Atividade": "Exercício voltado à discalculia: o aluno usa uma reta numérica física com marcadores móveis para resolver operações simples de adição e subtração.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "5º ano",
        _COL_DEF_REAL: "Dislexia / Discalculia",
        "Link do Vídeo/Conteúdo": "",
    },
    # --- Múltiplas deficiências / Outro ---
    {
        _COL_TITULO_REAL: "Estação multissensorial adaptável",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Estação com estímulos visuais, sonoros e táteis ajustáveis, permitindo que o professor combine recursos conforme as necessidades específicas de cada aluno.",
        "Idade Recomendada": "12-14 anos",
        "Série Escolar": "8º ano",
        _COL_DEF_REAL: "Múltiplas deficiências / Outro",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Planejamento individualizado: como adaptar uma atividade para múltiplas necessidades",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com um roteiro passo a passo para adaptar qualquer atividade da plataforma quando o aluno tem mais de uma condição associada.",
        "Idade Recomendada": "12-14 anos",
        "Série Escolar": "8º ano",
        _COL_DEF_REAL: "Múltiplas deficiências / Outro",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Ficha de adaptação personalizada",
        _COL_TIPO_CONTEUDO: "Exercício Didático",
        "Descrição da Atividade": "Modelo de ficha para o professor registrar quais adaptações (visual, motora, de comunicação) serão usadas em uma atividade específica.",
        "Idade Recomendada": "12-14 anos",
        "Série Escolar": "8º ano",
        _COL_DEF_REAL: "Múltiplas deficiências / Outro",
        "Link do Vídeo/Conteúdo": "",
    },

    # ------------------------------------------------------------
    # Exemplos adicionais (uma nova atividade e um novo artigo por
    # categoria), incluindo uma faixa etária/série diferente da já
    # cadastrada em cada categoria — isso amplia a cobertura dos
    # filtros de busca e evita que combinações de Idade + Série +
    # Deficiência "caiam num buraco" sem nenhum resultado.
    # ------------------------------------------------------------

    # --- TEA (Transtorno do Espectro Autista) ---
    {
        _COL_TITULO_REAL: "Quadro de emoções ilustrado",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Painel com rostos ilustrados representando emoções básicas, usado para o aluno apontar como está se sentindo ao longo do dia, apoiando a comunicação emocional.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "5º ano",
        _COL_DEF_REAL: "TEA (Transtorno do Espectro Autista)",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Comunicação sensorial: entendendo a hipersensibilidade a sons e luzes",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo explicando por que ambientes muito barulhentos ou com luzes fortes podem ser desconfortáveis para alunos autistas, com sugestões simples de ajuste do ambiente de sala.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "5º ano",
        _COL_DEF_REAL: "TEA (Transtorno do Espectro Autista)",
        "Link do Vídeo/Conteúdo": "",
    },

    # --- TDAH ---
    {
        _COL_TITULO_REAL: "Quadro de tarefas com cronômetro visual",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Cartaz com as tarefas do dia divididas em blocos curtos de tempo, usando um cronômetro visual (ampulheta ou disco colorido) para ajudar o aluno a perceber a passagem do tempo.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "TDAH",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Organização de tarefas em blocos curtos: um guia para famílias e professores",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com estratégias práticas para dividir tarefas longas em etapas menores e mais gerenciáveis, reduzindo a sobrecarga e melhorando a conclusão de atividades por alunos com TDAH.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "TDAH",
        "Link do Vídeo/Conteúdo": "",
    },

    # --- Deficiência Auditiva ---
    {
        _COL_TITULO_REAL: "Alfabeto manual ilustrado na parede da sala",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Cartaz ilustrado com o alfabeto manual em Libras fixado na sala, incentivando toda a turma a aprender e usar sinais básicos no dia a dia.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "1º ano",
        _COL_DEF_REAL: "Deficiência Auditiva",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Legendas e janela de Libras: tornando vídeos acessíveis em sala",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com orientações práticas para escolher ou adaptar vídeos educativos com legenda em português e janela de intérprete de Libras.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "1º ano",
        _COL_DEF_REAL: "Deficiência Auditiva",
        "Link do Vídeo/Conteúdo": "",
    },

    # --- Deficiência Visual ---
    {
        _COL_TITULO_REAL: "Caixa sonora de identificação",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Caixa com objetos do cotidiano que emitem sons característicos; o aluno identifica cada objeto apenas pelo som, estimulando percepção auditiva e vocabulário.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "4º ano",
        _COL_DEF_REAL: "Deficiência Visual",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Audiodescrição na prática: como narrar imagens e vídeos em sala de aula",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com um passo a passo simples para professores praticarem audiodescrição de imagens, gráficos e vídeos usados em aula, tornando o conteúdo visual acessível.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "4º ano",
        _COL_DEF_REAL: "Deficiência Visual",
        "Link do Vídeo/Conteúdo": "",
    },

    # --- Deficiência Física/Motora ---
    {
        _COL_TITULO_REAL: "Jogo de argolas com alvo ajustável",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Jogo de lançar argolas com altura e distância do alvo ajustáveis, permitindo que cada aluno participe no nível de esforço adequado à sua mobilidade.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "5º ano",
        _COL_DEF_REAL: "Deficiência Física/Motora",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Acessibilidade física na sala de aula: um checklist rápido",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com um checklist prático para avaliar e melhorar a acessibilidade física da sala — altura de mesas, largura de corredores, materiais ao alcance — para alunos com mobilidade reduzida.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "5º ano",
        _COL_DEF_REAL: "Deficiência Física/Motora",
        "Link do Vídeo/Conteúdo": "",
    },

    # --- Deficiência Intelectual / Síndrome de Down ---
    {
        _COL_TITULO_REAL: "Jogo de classificação por cores e formas",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Peças coloridas de formas variadas para o aluno classificar e agrupar, trabalhando raciocínio lógico e coordenação motora fina em um ritmo próprio.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "4º ano",
        _COL_DEF_REAL: "Deficiência Intelectual / Síndrome de Down",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Ensino estruturado: pequenos passos, grandes conquistas",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo sobre a importância de dividir conteúdos em etapas pequenas e concretas para alunos com deficiência intelectual, com exemplos de como celebrar cada conquista.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "4º ano",
        _COL_DEF_REAL: "Deficiência Intelectual / Síndrome de Down",
        "Link do Vídeo/Conteúdo": "",
    },

    # --- Dislexia / Discalculia ---
    {
        _COL_TITULO_REAL: "Jogo de rimas e sílabas com cartas ilustradas",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Cartas com imagens e palavras para o aluno formar rimas e separar sílabas em voz alta, reforçando a consciência fonológica de forma lúdica.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "3º ano",
        _COL_DEF_REAL: "Dislexia / Discalculia",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Discalculia no dia a dia: sinais de alerta e primeiros apoios",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo com sinais comuns de discalculia em sala de aula e primeiras estratégias de apoio, como uso de material concreto e mais tempo para resolver exercícios.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "3º ano",
        _COL_DEF_REAL: "Dislexia / Discalculia",
        "Link do Vídeo/Conteúdo": "",
    },

    # --- Múltiplas deficiências / Outro ---
    {
        _COL_TITULO_REAL: "Caixa de exploração multissensorial em dupla",
        _COL_TIPO_CONTEUDO: "Atividade",
        "Descrição da Atividade": "Atividade em dupla com objetos de texturas, cores e sons variados, incentivando a interação entre colegas e a exploração sensorial guiada pelo professor.",
        "Idade Recomendada": "3-5 anos",
        "Série Escolar": "Educação Infantil",
        _COL_DEF_REAL: "Múltiplas deficiências / Outro",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Plano Educacional Individualizado (PEI): por onde começar",
        _COL_TIPO_CONTEUDO: "Artigo",
        "Descrição da Atividade": "Artigo introdutório sobre o que é um Plano Educacional Individualizado, por que ele é importante quando o aluno tem mais de uma condição associada e como montar um em conjunto com a família.",
        "Idade Recomendada": "3-5 anos",
        "Série Escolar": "Educação Infantil",
        _COL_DEF_REAL: "Múltiplas deficiências / Outro",
        "Link do Vídeo/Conteúdo": "",
    },
])

# Preenche a ilustração de cada linha automaticamente, com base na
# categoria de deficiência/neurodivergência — assim toda atividade,
# artigo e exercício (novos e antigos) ganham a ilustração da sua
# categoria sem precisar repetir o campo em cada exemplo acima.
DADOS_EXEMPLO_ATIVIDADES[_COL_ILUSTRACAO] = DADOS_EXEMPLO_ATIVIDADES[_COL_DEF_REAL].map(_SVG_ILUSTRACOES)

DADOS_EXEMPLO_AVALIACOES = pd.DataFrame([
    {"Nome": "Profa. Marina", "Nota": 5, "Comentário": "Ferramenta simples e muito útil para achar ideias rápido."},
    {"Nome": "Coord. Pedro", "Nota": 4, "Comentário": "Gostaria de mais filtros por série escolar."},
    {"Nome": "Anônimo", "Nota": 5, "Comentário": "Os vídeos incorporados facilitam muito a vida em sala."},
])


# 4. FUNÇÃO PARA CARREGAR OS DADOS
@st.cache_data(ttl=60)
def load_data(url: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def carregar_atividades() -> pd.DataFrame:
    if MODO_TESTE:
        return DADOS_EXEMPLO_ATIVIDADES.copy()
    if _eh_placeholder(URL_RESPOSTAS_ATIVIDADES):
        return pd.DataFrame()
    df = load_data(URL_RESPOSTAS_ATIVIDADES)
    return df if not df.empty else DADOS_EXEMPLO_ATIVIDADES.copy()


def carregar_avaliacoes() -> pd.DataFrame:
    if MODO_TESTE:
        return DADOS_EXEMPLO_AVALIACOES.copy()
    if _eh_placeholder(URL_RESPOSTAS_AVALIACOES):
        return pd.DataFrame()
    return load_data(URL_RESPOSTAS_AVALIACOES)


df_atividades = carregar_atividades()

# 5. BARRA LATERAL (MENU E BOTÃO DE CADASTRO)
st.sidebar.title("Menu Principal")

if MODO_TESTE:
    st.sidebar.info("🧪 **Modo de teste ativo** — exibindo dados de exemplo. Configure os links do Google no topo de `app.py` e mude `MODO_TESTE` para `False` quando estiver pronto para usar dados reais.")

# Botão de chamada para ação em destaque
if _eh_placeholder(LINK_GOOGLE_FORMS_CADASTRO):
    st.sidebar.button("📤 Compartilhar Nova Atividade", disabled=True, use_container_width=True,
                       help="Configure LINK_GOOGLE_FORMS_CADASTRO em app.py para ativar este botão.")
else:
    st.sidebar.link_button("📤 Compartilhar Nova Atividade", LINK_GOOGLE_FORMS_CADASTRO, use_container_width=True)

st.sidebar.markdown("---")

# Sistema de navegação por abas
aba_selecionada = st.sidebar.radio(
    "Navegue pela plataforma:",
    ["Visualizar Atividades", "Estatísticas do Projeto", "Avaliar Plataforma"]
)

# --- ABA 1: VISUALIZAR ATIVIDADES ---
if aba_selecionada == "Visualizar Atividades":
    st.title("Ideias de Atividades Adaptadas")
    st.markdown("Use os filtros na barra lateral para encontrar os recursos ideais.")

    if not df_atividades.empty:
        # Filtros dinâmicos na barra lateral
        st.sidebar.subheader("Filtrar Conteúdo")

        # Garante existência das colunas esperadas
        col_idade = "Idade Recomendada"
        col_serie = "Série Escolar"
        col_def = _COL_DEF_REAL
        col_titulo = _COL_TITULO_REAL
        col_desc = "Descrição da Atividade"
        col_link = "Link do Vídeo/Conteúdo"
        col_tipo = _COL_TIPO_CONTEUDO
        col_ilustracao = _COL_ILUSTRACAO

        # Se a planilha tiver variações de nome, você pode mapear aqui:
        for col in [col_idade, col_serie, col_def, col_titulo, col_desc, col_link]:
            if col not in df_atividades.columns:
                st.sidebar.caption(f"⚠️ Coluna ausente na planilha: {col}")

        # ------------------------------------------------------------
        # Filtros em cascata (corrige o bug relatado de "nenhum
        # resultado encontrado"):
        #
        # Antes, os 4 filtros (Tipo, Idade, Série, Deficiência) eram
        # aplicados de forma independente sobre a lista completa de
        # atividades. Como cada categoria de deficiência tem sua
        # própria combinação fixa de idade/série, era fácil escolher
        # uma combinação (ex.: Idade = "6-8 anos" + Série = "1º ano" +
        # Deficiência = "Deficiência Física/Motora") que não existe em
        # nenhuma linha da planilha — e a busca retornava vazia, mesmo
        # existindo atividades para cada campo isoladamente.
        #
        # Agora cada filtro só mostra as opções que ainda existem
        # dentro do que já foi selecionado nos filtros anteriores. Ou
        # seja, é estruturalmente impossível chegar a uma combinação
        # sem resultado: as opções oferecidas sempre têm pelo menos
        # uma atividade correspondente.
        # ------------------------------------------------------------
        df_disponivel = df_atividades.copy()

        tipos_conteudo = ["Todos"] + sorted(list(df_disponivel.get(col_tipo, pd.Series(dtype=object)).dropna().unique()))
        tipo_sel = st.sidebar.selectbox("Tipo de Conteúdo", tipos_conteudo)
        if tipo_sel != "Todos" and col_tipo in df_disponivel.columns:
            df_disponivel = df_disponivel[df_disponivel[col_tipo].astype(str) == str(tipo_sel)]

        idades = ["Todos"] + sorted(list(df_disponivel.get(col_idade, pd.Series(dtype=object)).dropna().unique()))
        idade_sel = st.sidebar.selectbox("Idade", idades)
        if idade_sel != "Todos" and col_idade in df_disponivel.columns:
            df_disponivel = df_disponivel[df_disponivel[col_idade].astype(str) == str(idade_sel)]

        series = ["Todos"] + sorted(list(df_disponivel.get(col_serie, pd.Series(dtype=object)).dropna().unique()))
        serie_sel = st.sidebar.selectbox("Série Escolar", series)
        if serie_sel != "Todos" and col_serie in df_disponivel.columns:
            df_disponivel = df_disponivel[df_disponivel[col_serie].astype(str) == str(serie_sel)]

        deficiencias = ["Todos"] + sorted(list(df_disponivel.get(col_def, pd.Series(dtype=object)).dropna().unique()))
        # Rótulo mais acolhedor no filtro visível ao usuário: em vez de
        # "Foco/Deficiência", usamos "Perfil de Aprendizagem". Isso não
        # afeta os valores do filtro em si (que continuam sendo os nomes
        # técnicos corretos de cada categoria, como TEA, TDAH, Deficiência
        # Visual etc. — cada um preciso para a categoria que representa),
        # só a palavra usada no rótulo do campo.
        deficiencia_sel = st.sidebar.selectbox("Perfil de Aprendizagem", deficiencias)
        if deficiencia_sel != "Todos" and col_def in df_disponivel.columns:
            # regex=False é essencial aqui: o nome da categoria "TEA
            # (Transtorno do Espectro Autista)" contém parênteses, que
            # o pandas interpreta como sintaxe de regex por padrão. Sem
            # regex=False, filtrar justamente por essa categoria não
            # encontrava NENHUM resultado — nem os próprios exemplos de
            # TEA — porque os parênteses do padrão de busca não
            # correspondiam aos parênteses literais do texto. Esse era
            # o principal motivo do "nenhum resultado encontrado"
            # relatado pelos usuários.
            df_disponivel = df_disponivel[
                df_disponivel[col_def].astype(str).str.contains(str(deficiencia_sel), na=False, regex=False)
            ]

        df_filtrado = df_disponivel

        # Exibição dos resultados
        st.subheader(f"Recursos Disponíveis ({len(df_filtrado)})")

        if df_filtrado.empty:
            st.info("Nenhuma atividade corresponde aos filtros selecionados.")
        else:
            _EMOJI_TIPO = {"Atividade": "🎯", "Artigo": "📄", "Exercício Didático": "✏️"}

            for _, row in df_filtrado.iterrows():
                with st.container():
                    titulo = row.get(col_titulo, "Sem título")
                    desc = row.get(col_desc, "Sem descrição")
                    idade_v = row.get(col_idade, "N/A")
                    serie_v = row.get(col_serie, "N/A")
                    def_v = row.get(col_def, "N/A")
                    link = row.get(col_link, "")
                    ilustracao_v = row.get(col_ilustracao, "")
                    tipo_v = row.get(col_tipo, "Atividade")
                    if not (isinstance(tipo_v, str) and tipo_v.strip()):
                        tipo_v = "Atividade"
                    emoji_tipo = _EMOJI_TIPO.get(tipo_v, "🎯")

                    tem_ilustracao = isinstance(ilustracao_v, str) and ilustracao_v.strip()
                    if tem_ilustracao:
                        col_img, col_texto = st.columns([1, 4])
                        with col_img:
                            st.markdown(
                                f'<img src="{ilustracao_v}" alt="Ilustração da categoria" '
                                'style="width:100%;max-width:140px;border-radius:14px;" />',
                                unsafe_allow_html=True,
                            )
                    else:
                        col_texto = st.container()

                    with col_texto:
                        st.markdown(f"### {emoji_tipo} {titulo}")
                        st.caption(f"**Tipo de Conteúdo:** {tipo_v}")

                        c1, c2 = st.columns(2)
                        c1.caption(f"**Público:** {idade_v} | {serie_v}")
                        c2.caption(f"**Condição:** {def_v}")

                        st.write(desc)

                        if pd.notna(link) and str(link).strip():
                            if "youtube.com" in str(link) or "youtu.be" in str(link):
                                st.video(link)
                            else:
                                st.markdown(f"[Acessar Conteúdo Externo]({link})")

                    st.markdown("---")
    else:
        st.warning("Nenhuma atividade cadastrada ainda.")

# --- ABA 2: ESTATÍSTICAS DO PROJETO ---
elif aba_selecionada == "Estatísticas do Projeto":
    st.title("Indicadores da Plataforma")
    st.markdown("Dados em tempo real extraídos das colaborações da comunidade.")

    if not df_atividades.empty:
        # Métricas gerais em cards
        total_atividades = len(df_atividades)
        st.metric(label="Total de Atividades Cadastradas", value=total_atividades)

        col_grafico1, col_grafico2, col_grafico3 = st.columns(3)

        with col_grafico1:
            st.markdown("### Por Perfil de Aprendizagem")
            if _COL_DEF_REAL in df_atividades.columns:
                contagem_def = df_atividades[_COL_DEF_REAL].value_counts()
                st.bar_chart(contagem_def)
            else:
                st.caption(f"Coluna '{_COL_DEF_REAL}' não encontrada.")

        with col_grafico2:
            st.markdown("### Por Idade")
            if "Idade Recomendada" in df_atividades.columns:
                contagem_idade = df_atividades["Idade Recomendada"].value_counts()
                st.area_chart(contagem_idade)
            else:
                st.caption("Coluna 'Idade Recomendada' não encontrada.")

        with col_grafico3:
            st.markdown("### Por Tipo de Conteúdo")
            if _COL_TIPO_CONTEUDO in df_atividades.columns:
                contagem_tipo = df_atividades[_COL_TIPO_CONTEUDO].value_counts()
                st.bar_chart(contagem_tipo)
            else:
                st.caption(f"Coluna '{_COL_TIPO_CONTEUDO}' não encontrada.")
    else:
        st.info("Aguardando o envio de dados para gerar os gráficos.")

# --- ABA 3: AVALIAÇÃO DA PLATAFORMA ---
elif aba_selecionada == "Avaliar Plataforma":
    st.title("Sua opinião é fundamental")
    st.markdown("Ajude-nos a melhorar esta ferramenta acadêmica deixando o seu feedback.")

    col_esquerda, col_direita = st.columns([1, 2])

    with col_esquerda:
        st.markdown("### Deixe sua nota:")
        st.write("Criamos um formulário rápido para coletar notas de 1 a 5, sugestões e críticas de usabilidade.")
        if _eh_placeholder(LINK_GOOGLE_FORMS_AVALICAO):
            st.button("📝 Abrir Formulário de Avaliação", disabled=True,
                       help="Configure LINK_GOOGLE_FORMS_AVALICAO em app.py para ativar este botão.")
        else:
            st.link_button("📝 Abrir Formulário de Avaliação", LINK_GOOGLE_FORMS_AVALICAO, type="primary")

    with col_direita:
        st.markdown("### O que a comunidade está dizendo:")
        df_avaliacoes = carregar_avaliacoes()
        if not df_avaliacoes.empty:
            nome_col = "Nome" if "Nome" in df_avaliacoes.columns else df_avaliacoes.columns[0]
            nota_col = "Nota" if "Nota" in df_avaliacoes.columns else None
            coment_col = "Comentário" if "Comentário" in df_avaliacoes.columns else None

            for _, row in df_avaliacoes.tail(5).iterrows():
                nome = row.get(nome_col, "Anônimo")

                nota_bruta = row.get(nota_col) if nota_col else None
                try:
                    nota_val = int(nota_bruta) if pd.notna(nota_bruta) else 5
                except (TypeError, ValueError):
                    nota_val = 5
                estrelas = "⭐" * max(1, min(5, nota_val))

                comentario = row.get(coment_col) if coment_col else None
                if not (isinstance(comentario, str) and comentario.strip()):
                    comentario = "Sem comentários adicionais."

                st.markdown(f"**{nome}** - {estrelas}")
                st.caption(f"\"{comentario}\"")
                st.markdown("---")
        else:
            st.info("Seja o primeiro a avaliar o nosso projeto!")

# --- AVISO JURÍDICO FIXO NO FINAL DA BARRA LATERAL ---
st.sidebar.markdown("---")
st.sidebar.caption("**Aviso Legal:**")
st.sidebar.caption(
    "Esta plataforma funciona como um indexador comunitário de livre acesso. "
    "O conteúdo dos links e vídeos externos é de responsabilidade exclusiva de seus "
    "respectivos autores e das plataformas de origem (YouTube, Instagram, etc.)."
)
