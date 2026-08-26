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
        background-color: #4A90E2 !important;
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
])

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

        # Se a planilha tiver variações de nome, você pode mapear aqui:
        for col in [col_idade, col_serie, col_def, col_titulo, col_desc, col_link]:
            if col not in df_atividades.columns:
                st.sidebar.caption(f"⚠️ Coluna ausente na planilha: {col}")

        tipos_conteudo = ["Todos"] + sorted(list(df_atividades.get(col_tipo, pd.Series(dtype=object)).dropna().unique()))
        tipo_sel = st.sidebar.selectbox("Tipo de Conteúdo", tipos_conteudo)

        idades = ["Todos"] + sorted(list(df_atividades.get(col_idade, pd.Series(dtype=object)).dropna().unique()))
        idade_sel = st.sidebar.selectbox("Idade", idades)

        series = ["Todos"] + sorted(list(df_atividades.get(col_serie, pd.Series(dtype=object)).dropna().unique()))
        serie_sel = st.sidebar.selectbox("Série Escolar", series)

        deficiencias = ["Todos"] + sorted(list(df_atividades.get(col_def, pd.Series(dtype=object)).dropna().unique()))
        deficiencia_sel = st.sidebar.selectbox("Foco/Deficiência", deficiencias)

        # Lógica de filtragem
        df_filtrado = df_atividades.copy()

        if tipo_sel != "Todos" and col_tipo in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado[col_tipo].astype(str) == str(tipo_sel)]

        if idade_sel != "Todos" and col_idade in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado[col_idade].astype(str) == str(idade_sel)]

        if serie_sel != "Todos" and col_serie in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado[col_serie].astype(str) == str(serie_sel)]

        if deficiencia_sel != "Todos" and col_def in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado[col_def].astype(str).str.contains(str(deficiencia_sel), na=False)]

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
                    tipo_v = row.get(col_tipo, "Atividade")
                    if not (isinstance(tipo_v, str) and tipo_v.strip()):
                        tipo_v = "Atividade"
                    emoji_tipo = _EMOJI_TIPO.get(tipo_v, "🎯")

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
            st.markdown("### Por Tipo de Deficiência")
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
