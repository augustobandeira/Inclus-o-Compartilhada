import streamlit as st
import pandas as pd

# ============================================================
# INCLUSÃO COMPARTILHADA
# Painel de atividades pedagógicas inclusivas, alimentado por
# Google Forms + Google Planilhas.
# ============================================================

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Inclusão Compartilhada", page_icon="🧩", layout="wide")

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
_COL_TITULO_REAL = "Título da atividade"
_COL_DEF_REAL = "Para qual tipo de deficiência ou neurodivergência esta atividade foi pensada?"

DADOS_EXEMPLO_ATIVIDADES = pd.DataFrame([
    {
        _COL_TITULO_REAL: "Caça ao tesouro sensorial",
        "Descrição da Atividade": "Circuito com texturas, sons e cheiros variados para exploração sensorial guiada, com rotina visual antecipando cada estação.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "1º ano",
        _COL_DEF_REAL: "TEA (Transtorno do Espectro Autista)",
        "Link do Vídeo/Conteúdo": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    },
    {
        _COL_TITULO_REAL: "Corrida dos números com pausas ativas",
        "Descrição da Atividade": "Atividade de matemática com deslocamento físico entre estações, pensada para manter o foco e permitir gasto de energia.",
        "Idade Recomendada": "9-11 anos",
        "Série Escolar": "4º ano",
        _COL_DEF_REAL: "TDAH",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Contação de histórias em Libras",
        "Descrição da Atividade": "História narrada em Libras com apoio de imagens e legenda simultânea em português.",
        "Idade Recomendada": "3-5 anos",
        "Série Escolar": "Educação Infantil",
        _COL_DEF_REAL: "Deficiência Auditiva",
        "Link do Vídeo/Conteúdo": "https://youtu.be/dQw4w9WgXcQ",
    },
    {
        _COL_TITULO_REAL: "Mapa tátil do bairro",
        "Descrição da Atividade": "Maquete tátil com texturas diferentes representando ruas, praças e pontos de referência do entorno da escola.",
        "Idade Recomendada": "12-14 anos",
        "Série Escolar": "7º ano",
        _COL_DEF_REAL: "Deficiência Visual",
        "Link do Vídeo/Conteúdo": "",
    },
    {
        _COL_TITULO_REAL: "Comunicação alternativa no recreio",
        "Descrição da Atividade": "Cartões de Comunicação Alternativa (CAA) plastificados para mediar brincadeiras coletivas no intervalo.",
        "Idade Recomendada": "6-8 anos",
        "Série Escolar": "2º ano",
        _COL_DEF_REAL: "Deficiência Intelectual / Síndrome de Down",
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

        # Se a planilha tiver variações de nome, você pode mapear aqui:
        for col in [col_idade, col_serie, col_def, col_titulo, col_desc, col_link]:
            if col not in df_atividades.columns:
                st.sidebar.caption(f"⚠️ Coluna ausente na planilha: {col}")

        idades = ["Todos"] + sorted(list(df_atividades.get(col_idade, pd.Series(dtype=object)).dropna().unique()))
        idade_sel = st.sidebar.selectbox("Idade", idades)

        series = ["Todos"] + sorted(list(df_atividades.get(col_serie, pd.Series(dtype=object)).dropna().unique()))
        serie_sel = st.sidebar.selectbox("Série Escolar", series)

        deficiencias = ["Todos"] + sorted(list(df_atividades.get(col_def, pd.Series(dtype=object)).dropna().unique()))
        deficiencia_sel = st.sidebar.selectbox("Foco/Deficiência", deficiencias)

        # Lógica de filtragem
        df_filtrado = df_atividades.copy()

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
            for _, row in df_filtrado.iterrows():
                with st.container():
                    titulo = row.get(col_titulo, "Sem título")
                    desc = row.get(col_desc, "Sem descrição")
                    idade_v = row.get(col_idade, "N/A")
                    serie_v = row.get(col_serie, "N/A")
                    def_v = row.get(col_def, "N/A")
                    link = row.get(col_link, "")

                    st.markdown(f"### {titulo}")

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

        col_grafico1, col_grafico2 = st.columns(2)

        with col_grafico1:
            st.markdown("### Atividades por Tipo de Deficiência")
            if _COL_DEF_REAL in df_atividades.columns:
                contagem_def = df_atividades[_COL_DEF_REAL].value_counts()
                st.bar_chart(contagem_def)
            else:
                st.caption(f"Coluna '{_COL_DEF_REAL}' não encontrada.")

        with col_grafico2:
            st.markdown("### Distribuição por Idade")
            if "Idade Recomendada" in df_atividades.columns:
                contagem_idade = df_atividades["Idade Recomendada"].value_counts()
                st.area_chart(contagem_idade)
            else:
                st.caption("Coluna 'Idade Recomendada' não encontrada.")
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
