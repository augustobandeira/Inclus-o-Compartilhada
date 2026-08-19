import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# ======================================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ======================================================================================
st.set_page_config(page_title="Inclusão Compartilhada", page_icon="🧩", layout="wide")

# ======================================================================================
# 1.1 AJUSTES DE RESPONSIVIDADE (CELULAR)
# ======================================================================================
# O Streamlit já é responsivo por padrão (colunas empilham e o menu lateral vira um
# ícone "☰" em telas estreitas), mas alguns ajustes finos deixam a experiência em
# smartphone mais confortável: espaçamentos menores, textos com leitura mais fácil,
# botões com área de toque maior e cards que não "estouram" a largura da tela.
st.markdown(
    """
    <style>
    /* Reduz o espaçamento lateral excessivo em telas pequenas */
    @media (max-width: 640px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1.2rem;
        }
        h1 { font-size: 1.5rem !important; }
        h2, h3 { font-size: 1.15rem !important; }
        /* Cards de atividade com menos padding interno em telas estreitas */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 0.25rem 0 !important;
        }
    }

    /* Área de toque maior para botões e itens de seleção (bom em qualquer tela,
       essencial no toque do celular) */
    button, [data-testid="stSelectbox"] > div, [data-testid="stTextInput"] input {
        min-height: 44px;
    }

    /* Evita que textos longos (títulos, tags) estourem a largura do card */
    div[data-testid="stVerticalBlockBorderWrapper"] * {
        overflow-wrap: break-word;
    }

    /* Botão de compartilhar mais confortável para o polegar no celular */
    [data-testid="stSidebar"] button {
        min-height: 46px;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🧪 MODO DE TESTE — deixe True para usar o CSV local abaixo em vez da planilha do
# Google. Quando for usar o formulário real, mude para False.
MODO_TESTE = True
CSV_TESTE = "atividades_cadastradas.csv"

# ⚠️ SUBSTITUA os valores abaixo pelos links reais do seu Google Forms e das planilhas
# publicadas em CSV (Arquivo > Compartilhar > Publicar na Web > CSV, no Google Sheets).
URL_RESPOSTAS_ATIVIDADES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSkm00K4FLV_GAnJrli0Laqt4-hv35oFz14OgdRIvicxWEV0EOX8hHx1ijNVqk8uqklUKfjeKrSTFVi/pub?gid=1764416550&single=true&output=csv"
LINK_GOOGLE_FORMS_CADASTRO = "https://google.com"   # substitua pelo link do seu Forms de cadastro
LINK_GOOGLE_FORMS_AVALICAO = "https://google.com"   # substitua pelo link do seu Forms de avaliação
URL_RESPOSTAS_AVALIACOES = "https://docs.google.com/spreadsheets/d/e/2PACX-XXXXXXXXXXXXX/pub?gid=0&single=true&output=csv"

# ======================================================================================
# Esquemas de coluna suportados
# ======================================================================================
# O app aceita dois formatos de planilha de atividades: o "novo" (formulário rico,
# organizado por tipo de deficiência/neurodivergência) e o "legado" (formulário simples
# usado antes). O esquema é detectado automaticamente pela presença da coluna
# "Faixa Etária-Alvo", exclusiva do formulário novo.

SCHEMA_NOVO = {
    "titulo": "Título da Atividade",
    "idade": "Faixa Etária-Alvo",
    "serie": "Série(s)/Ano(s) Escolar(es)",
    "deficiencia": "Tipo(s) de Deficiência/Neurodivergência",
    "componente": "Componente Curricular",
    "tipo_turma": "Tipo de Turma",
    "mediacao": "Mediação Técnica Necessária",
    "formato": "Formato da Atividade",
    "tempo": "Tempo Estimado de Duração",
    "objetivo": "Objetivo da Atividade",
    "passos": "Passos/Procedimentos da Atividade",
    "materiais": "Materiais/Recursos Necessários",
    "adaptacoes": "Adaptações Realizadas",
    "avaliacao": "Avaliação/Aprendizagem",
    "palavras_chave": "Palavras-Chave",
    "arquivo_disp": "Arquivo Disponível para Download",
    "formato_arquivo": "Formato do Arquivo",
    "comentarios": "Comentários/Observações",
    "autor": "Nome para Exibição",
    "profissao": "Profissão/Cargo",
    "esfera": "Esfera de Atuação",
}

SCHEMA_LEGADO = {
    "titulo": "Título da Atividade",
    "idade": "Idade Recomendada",
    "serie": "Série Escolar",
    "deficiencia": "Tipo de Deficiência/Neurodivergência",
    "descricao": "Descrição da Atividade",
    "link": "Link do Vídeo/Conteúdo",
}

# Colunas cujo conteúdo pode ter múltiplos valores separados por "; "
COLUNAS_MULTIVALOR = {"serie", "deficiencia"}

# Colunas esperadas na planilha de avaliações.
COL_NOME = "Nome"
COL_NOTA = "Nota"
COL_COMENTARIO = "Comentário"


def detectar_schema(df: pd.DataFrame) -> dict:
    """Detecta automaticamente se a planilha carregada usa o formulário novo (rico) ou
    o formulário legado (simples), com base nas colunas presentes."""
    if SCHEMA_NOVO["idade"] in df.columns:
        return SCHEMA_NOVO
    return SCHEMA_LEGADO


def col(schema: dict, chave: str) -> str | None:
    """Atalho seguro para obter o nome real da coluna a partir da chave lógica."""
    return schema.get(chave)


def split_multivalor(texto: str) -> list:
    """Divide uma string em itens separados por ';', mas ignora ';' que estejam dentro
    de parênteses — usados nos dados para exemplificar/detalhar uma mesma categoria
    (ex.: "Transtorno de Aprendizagem (Dislexia; Discalculia; Disgrafia)" é UM item, não três)."""
    itens, atual, profundidade = [], [], 0
    for ch in str(texto):
        if ch == "(":
            profundidade += 1
            atual.append(ch)
        elif ch == ")":
            profundidade = max(0, profundidade - 1)
            atual.append(ch)
        elif ch == ";" and profundidade == 0:
            itens.append("".join(atual).strip())
            atual = []
        else:
            atual.append(ch)
    if atual:
        itens.append("".join(atual).strip())
    return [i for i in itens if i]


def valores_unicos(df: pd.DataFrame, coluna: str, multivalor: bool) -> list:
    """Retorna os valores únicos de uma coluna para popular filtros. Se a coluna for
    multivalorada (itens separados por '; ', respeitando parênteses), primeiro
    'explode' os valores."""
    serie = df[coluna].dropna().astype(str)
    if multivalor:
        todos = []
        for v in serie:
            todos.extend(split_multivalor(v))
        return sorted(set(todos))
    return sorted(serie.unique())


def gerar_url_incorporada(url_forms: str) -> str:
    """Converte o link normal de um Google Forms (.../viewform?...) no link incorporável
    (.../viewform?embedded=true), usado para exibir o formulário direto dentro do app
    via iframe, sem o usuário precisar sair da página."""
    if "embedded=true" in url_forms:
        return url_forms
    separador = "&" if "?" in url_forms else "?"
    return f"{url_forms}{separador}embedded=true"


def url_e_placeholder(url: str) -> bool:
    """Detecta se a URL ainda é um valor de exemplo/placeholder e não foi configurada."""
    if not url or not str(url).strip():
        return True
    url = url.strip()
    if url.rstrip("/") in ("https://google.com", "http://google.com"):
        return True
    marcadores = ["XXXXXXXXXXXXX", "SUA_PLANILHA", "COLE_AQUI", "URL_DA_SUA_PLANILHA"]
    return any(m in url for m in marcadores)


# ======================================================================================
# 2. FUNÇÃO PARA CARREGAR OS DADOS
# ======================================================================================
@st.cache_data(ttl=60, show_spinner=False)
def load_data(url: str) -> pd.DataFrame:
    """Carrega uma planilha publicada como CSV. Retorna DataFrame vazio em caso de erro,
    sem derrubar o app."""
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        return pd.DataFrame()


def carregar_com_aviso(url: str, nome_amigavel: str, csv_local: str = None) -> pd.DataFrame:
    """Envolve load_data com mensagens claras para quem estiver configurando o app.
    Se MODO_TESTE estiver ativo e um csv_local for informado, carrega dali em vez da URL."""
    if MODO_TESTE and csv_local:
        try:
            df_local = pd.read_csv(csv_local)
            df_local.columns = df_local.columns.str.strip()
            return df_local
        except FileNotFoundError:
            st.error(
                f"❌ Modo de teste ativo, mas não encontrei o arquivo `{csv_local}` na pasta do projeto. "
                f"Coloque o CSV ao lado do `app.py` ou desative o MODO_TESTE."
            )
            return pd.DataFrame()

    if url_e_placeholder(url):
        st.info(
            f"ℹ️ A planilha de **{nome_amigavel}** ainda não foi configurada. "
            f"Publique sua planilha do Google (Arquivo → Compartilhar → Publicar na Web → CSV) "
            f"e cole o link no topo do `app.py`."
        )
        return pd.DataFrame()

    with st.spinner(f"Carregando {nome_amigavel.lower()}..."):
        df = load_data(url)

    if df.empty:
        st.warning(
            f"⚠️ Não consegui carregar a planilha de **{nome_amigavel}** agora. "
            f"Verifique se o link continua público e no formato CSV, e tente recarregar a página."
        )
    return df


df_atividades = carregar_com_aviso(URL_RESPOSTAS_ATIVIDADES, "Atividades", csv_local=CSV_TESTE)
schema = detectar_schema(df_atividades) if not df_atividades.empty else SCHEMA_NOVO
eh_schema_novo = schema is SCHEMA_NOVO

# ======================================================================================
# 3. BARRA LATERAL (MENU E BOTÃO DE CADASTRO)
# ======================================================================================
st.sidebar.title("🧩 Menu Principal")

aba_selecionada = st.sidebar.radio(
    "Navegue pela plataforma:",
    [
        "📚 Visualizar Atividades",
        "📤 Compartilhar Nova Atividade",
        "📊 Estatísticas do Projeto",
        "⭐ Avaliar Plataforma",
    ],
)

st.sidebar.markdown("---")

# ======================================================================================
# ABA 1: VISUALIZAR ATIVIDADES
# ======================================================================================
if aba_selecionada == "📚 Visualizar Atividades":
    st.title("Ideias de Atividades Adaptadas")
    st.markdown("Use os filtros na barra lateral para encontrar os recursos ideais.")
    st.caption("📱 No celular, toque no ícone **☰** no canto superior esquerdo para abrir os filtros.")

    colunas_essenciais = [schema["titulo"], schema["idade"], schema["serie"], schema["deficiencia"]]
    colunas_faltando = [c for c in colunas_essenciais if c not in df_atividades.columns]

    if not df_atividades.empty and colunas_faltando:
        st.error(
            "❌ Sua planilha foi carregada, mas está faltando a(s) coluna(s): "
            + ", ".join(f"**{c}**" for c in colunas_faltando)
            + ". Confira se os títulos das colunas no Google Forms/Sheets batem exatamente "
            "com os nomes esperados no `app.py`."
        )

    if not df_atividades.empty and not colunas_faltando:
        st.sidebar.subheader("🔍 Filtrar Conteúdo")

        busca = st.sidebar.text_input("Buscar por palavra-chave")

        idades = ["Todos"] + valores_unicos(df_atividades, schema["idade"], "idade" in COLUNAS_MULTIVALOR)
        idade_sel = st.sidebar.selectbox("Idade", idades)

        series = ["Todos"] + valores_unicos(df_atividades, schema["serie"], "serie" in COLUNAS_MULTIVALOR)
        serie_sel = st.sidebar.selectbox("Série Escolar", series)

        deficiencias = ["Todos"] + valores_unicos(df_atividades, schema["deficiencia"], "deficiencia" in COLUNAS_MULTIVALOR)
        deficiencia_sel = st.sidebar.selectbox("Foco/Deficiência", deficiencias)

        # Filtros avançados extras, disponíveis apenas no formulário novo
        componente_sel, formato_sel = "Todos", "Todos"
        if eh_schema_novo:
            with st.sidebar.expander("⚙️ Filtros avançados"):
                if schema["componente"] in df_atividades.columns:
                    componentes = ["Todos"] + valores_unicos(df_atividades, schema["componente"], False)
                    componente_sel = st.selectbox("Componente Curricular", componentes)
                if schema["formato"] in df_atividades.columns:
                    formatos = ["Todos"] + valores_unicos(df_atividades, schema["formato"], False)
                    formato_sel = st.selectbox("Formato da Atividade", formatos)

        df_filtrado = df_atividades.copy()

        if idade_sel != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado[schema["idade"]].astype(str).str.contains(idade_sel, case=False, na=False, regex=False)
            ]
        if serie_sel != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado[schema["serie"]].astype(str).str.contains(serie_sel, case=False, na=False, regex=False)
            ]
        if deficiencia_sel != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado[schema["deficiencia"]].astype(str).str.contains(deficiencia_sel, case=False, na=False, regex=False)
            ]
        if componente_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado[schema["componente"]].astype(str) == componente_sel]
        if formato_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado[schema["formato"]].astype(str) == formato_sel]
        if busca:
            colunas_busca = [schema["titulo"]]
            colunas_busca.append(schema.get("objetivo") or schema.get("descricao"))
            mascara = pd.Series(False, index=df_filtrado.index)
            for c in colunas_busca:
                if c and c in df_filtrado.columns:
                    mascara |= df_filtrado[c].astype(str).str.contains(busca, case=False, na=False)
            df_filtrado = df_filtrado[mascara]

        st.subheader(f"Recursos Disponíveis ({len(df_filtrado)})")

        if df_filtrado.empty:
            st.info("Nenhuma atividade corresponde aos filtros selecionados. Tente ajustar ou limpar os filtros.")
        else:
            for _, row in df_filtrado.iterrows():
                with st.container(border=True):
                    titulo = row.get(schema["titulo"]) or "Sem título"
                    idade_v = row.get(schema["idade"]) or "N/A"
                    serie_v = row.get(schema["serie"]) or "N/A"
                    def_v = row.get(schema["deficiencia"]) or "N/A"

                    st.markdown(f"### {titulo}")

                    c1, c2 = st.columns(2)
                    c1.caption(f"**Público:** {idade_v} | {serie_v}")
                    c2.caption(f"**Foco:** {def_v}")

                    if eh_schema_novo:
                        # ---- Cartão completo do formulário novo ----
                        tags = []
                        if row.get(schema["componente"]):
                            tags.append(f"📘 {row[schema['componente']]}")
                        if row.get(schema["formato"]):
                            tags.append(f"🧩 {row[schema['formato']]}")
                        if row.get(schema["tempo"]):
                            tags.append(f"⏱️ {row[schema['tempo']]}")
                        if row.get(schema["tipo_turma"]):
                            tags.append(f"👥 {row[schema['tipo_turma']]}")
                        if tags:
                            st.caption(" · ".join(tags))

                        if row.get(schema["objetivo"]):
                            st.write(f"**Objetivo:** {row[schema['objetivo']]}")

                        with st.expander("Ver detalhes completos da atividade"):
                            if row.get(schema["passos"]):
                                st.markdown("**Passos/Procedimentos:**")
                                st.write(row[schema["passos"]])
                            if row.get(schema["materiais"]):
                                st.markdown("**Materiais/Recursos Necessários:**")
                                st.write(row[schema["materiais"]])
                            if row.get(schema["adaptacoes"]):
                                st.markdown("**Adaptações Realizadas:**")
                                st.write(row[schema["adaptacoes"]])
                            if row.get(schema["avaliacao"]):
                                st.markdown(f"**Avaliação/Aprendizagem:** {row[schema['avaliacao']]}")
                            if row.get(schema["mediacao"]):
                                st.markdown(f"**Mediação Técnica Necessária:** {row[schema['mediacao']]}")
                            if row.get(schema["palavras_chave"]):
                                st.markdown(f"**Palavras-chave:** {row[schema['palavras_chave']]}")
                            if row.get(schema["comentarios"]):
                                st.markdown(f"**Comentários:** {row[schema['comentarios']]}")

                            arquivo_disp = str(row.get(schema["arquivo_disp"], "")).strip().lower()
                            if arquivo_disp == "sim":
                                formato_arq = row.get(schema["formato_arquivo"]) or "formato não informado"
                                st.info(f"📎 Esta atividade possui arquivo de apoio disponível ({formato_arq}) — solicite ao autor pelo e-mail informado no cadastro.")

                            autor = row.get(schema["autor"])
                            profissao = row.get(schema["profissao"])
                            if autor:
                                rodape = f"Compartilhado por **{autor}**"
                                if profissao:
                                    rodape += f" · {profissao}"
                                st.caption(rodape)
                    else:
                        # ---- Cartão simples do formulário legado ----
                        desc = row.get(schema.get("descricao")) or "Sem descrição"
                        st.write(desc)
                        link = row.get(schema.get("link"))
                        if pd.notna(link) and str(link).strip():
                            link_str = str(link).strip()
                            if "youtube.com" in link_str or "youtu.be" in link_str:
                                st.video(link_str)
                            else:
                                st.markdown(f"[🔗 Acessar Conteúdo Externo]({link_str})")
    elif df_atividades.empty and not url_e_placeholder(URL_RESPOSTAS_ATIVIDADES):
        st.warning("Nenhuma atividade cadastrada ainda. Seja o primeiro a compartilhar uma!")

# ======================================================================================
# ABA NOVA: COMPARTILHAR NOVA ATIVIDADE (formulário nativo do Streamlit)
# ======================================================================================
elif aba_selecionada == "📤 Compartilhar Nova Atividade":
    st.title("Compartilhar uma Nova Atividade")
    st.markdown(
        "Contribua com o acervo do **Inclusão Compartilhada** enviando uma atividade "
        "pedagógica adaptada. As informações serão usadas nos filtros por idade, série "
        "e deficiência ou neurodivergência."
    )
    st.info(
        "Não informe nomes, imagens, diagnósticos individuais ou outros dados que "
        "permitam identificar crianças ou estudantes. Campos com * são obrigatórios."
    )

    with st.form("form_cadastro_atividade", clear_on_submit=True):
        st.subheader("1. Identificação e objetivo")
        titulo = st.text_input("Título da atividade *", max_chars=120)
        objetivo = st.text_area(
            "Qual é o objetivo pedagógico da atividade? *",
            max_chars=1000,
            placeholder="Descreva as aprendizagens ou habilidades que se pretende desenvolver.",
        )
        componente = st.selectbox(
            "Componente curricular *",
            ["Selecione", "Alfabetização e Linguagens", "Matemática", "Ciências",
             "História", "Geografia", "Artes", "Educação Física", "Socioemocional",
             "Autonomia e Vida Diária", "Tecnologia", "Interdisciplinar", "Outro"],
        )

        st.subheader("2. Público da atividade")
        c1, c2 = st.columns(2)
        with c1:
            idade = st.selectbox(
                "Faixa etária-alvo *",
                ["Selecione", "0 a 3 anos", "4 a 5 anos", "6 a 8 anos", "9 a 11 anos",
                 "12 a 14 anos", "15 a 17 anos", "18 anos ou mais"],
            )
        with c2:
            series = st.multiselect(
                "Série(s)/ano(s) escolar(es) *",
                ["Educação Infantil", "1º ano", "2º ano", "3º ano", "4º ano", "5º ano",
                 "6º ano", "7º ano", "8º ano", "9º ano", "Ensino Médio", "EJA",
                 "Atendimento Educacional Especializado", "Não se aplica"],
            )
        deficiencias = st.multiselect(
            "Tipo(s) de deficiência, neurodivergência ou necessidade contemplada(s) *",
            ["Transtorno do Espectro Autista (TEA)", "TDAH", "Dislexia", "Discalculia",
             "Deficiência Intelectual", "Deficiência Visual", "Deficiência Auditiva",
             "Deficiência Física", "Deficiência Múltipla", "Altas Habilidades/Superdotação",
             "Dificuldades de Comunicação", "Dificuldades Socioemocionais",
             "Aplicável a diferentes perfis", "Outra"],
        )

        st.subheader("3. Organização e aplicação")
        c3, c4 = st.columns(2)
        with c3:
            tipo_turma = st.selectbox(
                "Como a atividade pode ser realizada? *",
                ["Selecione", "Individual", "Em dupla", "Em pequenos grupos",
                 "Com toda a turma", "Flexível"],
            )
            formato = st.selectbox(
                "Formato da atividade *",
                ["Selecione", "Impressa", "Digital", "Jogo", "Sensorial", "Prática",
                 "Dinâmica", "Projeto", "Outro"],
            )
        with c4:
            mediacao = st.selectbox(
                "Qual mediação é necessária? *",
                ["Selecione", "Baixa", "Moderada", "Intensa", "Depende do estudante"],
            )
            tempo = st.selectbox(
                "Tempo estimado de duração *",
                ["Selecione", "Até 15 minutos", "16 a 30 minutos", "31 a 45 minutos",
                 "46 a 60 minutos", "Mais de 60 minutos", "Mais de um encontro"],
            )
        passos = st.text_area(
            "Quais são os passos ou procedimentos da atividade? *",
            height=180,
            placeholder="Explique a preparação, a aplicação e a conclusão da atividade.",
        )
        materiais = st.text_area("Quais materiais ou recursos são necessários? *")
        adaptacoes = st.text_area(
            "Quais adaptações de acessibilidade foram realizadas? *",
            placeholder="Ex.: pictogramas, material tátil, fonte ampliada, tempo adicional ou comunicação alternativa.",
        )
        avaliacao = st.text_area(
            "Como a aprendizagem ou a participação pode ser avaliada? *",
            placeholder="Descreva critérios de observação, registro ou acompanhamento.",
        )

        st.subheader("4. Complementos e autoria")
        palavras_chave = st.text_input(
            "Palavras-chave",
            placeholder="Separe por vírgulas. Ex.: emoções, comunicação, interação social",
        )
        arquivo_disp = st.radio(
            "Existe arquivo ou material de apoio disponível?",
            ["Não", "Sim"], horizontal=True,
        )
        formato_arquivo = st.text_input(
            "Formato do arquivo, se houver",
            placeholder="Ex.: PDF, DOCX, PPTX ou link público",
        )
        comentarios = st.text_area("Comentários, cuidados ou recomendações adicionais")
        c5, c6 = st.columns(2)
        with c5:
            autor = st.text_input("Nome para exibição", max_chars=100)
            profissao = st.text_input("Profissão ou cargo")
        with c6:
            esfera = st.selectbox(
                "Esfera de atuação",
                ["Não informar", "Educação pública", "Educação privada", "Ensino superior",
                 "Família ou comunidade", "Saúde", "Outra"],
            )

        autorizacao = st.checkbox(
            "Declaro que posso compartilhar este conteúdo e que não incluí dados pessoais de crianças ou estudantes. *"
        )
        enviar = st.form_submit_button("Enviar atividade", type="primary", use_container_width=True)

    if enviar:
        obrigatorios = [
            titulo.strip(), objetivo.strip(), componente != "Selecione", idade != "Selecione",
            bool(series), bool(deficiencias), tipo_turma != "Selecione", formato != "Selecione",
            mediacao != "Selecione", tempo != "Selecione", passos.strip(), materiais.strip(),
            adaptacoes.strip(), avaliacao.strip(), autorizacao,
        ]
        if not all(obrigatorios):
            st.error("Preencha todos os campos obrigatórios e aceite a declaração de compartilhamento.")
        else:
            registro = {
                "Data de Envio": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Título da Atividade": titulo.strip(),
                "Faixa Etária-Alvo": idade,
                "Série(s)/Ano(s) Escolar(es)": "; ".join(series),
                "Tipo(s) de Deficiência/Neurodivergência": "; ".join(deficiencias),
                "Componente Curricular": componente,
                "Tipo de Turma": tipo_turma,
                "Mediação Técnica Necessária": mediacao,
                "Formato da Atividade": formato,
                "Tempo Estimado de Duração": tempo,
                "Objetivo da Atividade": objetivo.strip(),
                "Passos/Procedimentos da Atividade": passos.strip(),
                "Materiais/Recursos Necessários": materiais.strip(),
                "Adaptações Realizadas": adaptacoes.strip(),
                "Avaliação/Aprendizagem": avaliacao.strip(),
                "Palavras-Chave": palavras_chave.strip(),
                "Arquivo Disponível para Download": arquivo_disp,
                "Formato do Arquivo": formato_arquivo.strip(),
                "Comentários/Observações": comentarios.strip(),
                "Nome para Exibição": autor.strip() or "Anônimo",
                "Profissão/Cargo": profissao.strip(),
                "Esfera de Atuação": esfera,
            }
            destino = Path(CSV_TESTE)
            novo = pd.DataFrame([registro])
            novo.to_csv(
                destino, mode="a" if destino.exists() else "w",
                header=not destino.exists(), index=False, encoding="utf-8-sig",
            )
            st.cache_data.clear()
            st.success("Atividade enviada com sucesso e adicionada ao acervo!")
            st.caption("Atualize a página para visualizar imediatamente o novo registro nos filtros e indicadores.")

# ======================================================================================
# ABA 2: ESTATÍSTICAS DO PROJETO
# ======================================================================================
elif aba_selecionada == "📊 Estatísticas do Projeto":
    st.title("Indicadores da Plataforma")
    st.markdown("Dados em tempo real extraídos das colaborações da comunidade.")

    if not df_atividades.empty:
        total_atividades = len(df_atividades)
        col_a, col_b = st.columns(2)
        col_a.metric(label="Total de Atividades Cadastradas", value=total_atividades)

        if schema["deficiencia"] in df_atividades.columns:
            focos_unicos = valores_unicos(df_atividades, schema["deficiencia"], True)
            col_b.metric(label="Focos/Deficiências Cobertos", value=len(focos_unicos))

        col_grafico1, col_grafico2 = st.columns(2)

        with col_grafico1:
            st.markdown("### Atividades por Tipo de Deficiência")
            if schema["deficiencia"] in df_atividades.columns and df_atividades[schema["deficiencia"]].notna().any():
                todos_tokens = []
                for v in df_atividades[schema["deficiencia"]].dropna().astype(str):
                    todos_tokens.extend(split_multivalor(v))
                st.bar_chart(pd.Series(todos_tokens).value_counts())
            else:
                st.caption(f"Coluna '{schema['deficiencia']}' não encontrada ou vazia.")

        with col_grafico2:
            st.markdown("### Distribuição por Idade")
            if schema["idade"] in df_atividades.columns and df_atividades[schema["idade"]].notna().any():
                st.area_chart(df_atividades[schema["idade"]].value_counts())
            else:
                st.caption(f"Coluna '{schema['idade']}' não encontrada ou vazia.")

        if eh_schema_novo and schema["componente"] in df_atividades.columns:
            st.markdown("### Atividades por Componente Curricular")
            st.bar_chart(df_atividades[schema["componente"]].value_counts())
    else:
        st.info("Aguardando o envio de dados para gerar os gráficos.")

# ======================================================================================
# ABA 3: AVALIAÇÃO DA PLATAFORMA
# ======================================================================================
elif aba_selecionada == "⭐ Avaliar Plataforma":
    st.title("Sua opinião é fundamental")
    st.markdown("Ajude-nos a melhorar esta ferramenta acadêmica deixando o seu feedback.")

    col_esquerda, col_direita = st.columns([1, 2])

    with col_esquerda:
        st.markdown("### Deixe sua nota:")
        st.write("Criamos um formulário rápido para coletar notas de 1 a 5, sugestões e críticas de usabilidade.")

        if url_e_placeholder(LINK_GOOGLE_FORMS_AVALICAO):
            st.info(
                "ℹ️ O link do formulário de avaliação ainda não foi configurado. "
                "Substitua `LINK_GOOGLE_FORMS_AVALICAO` no topo do `app.py`."
            )
        else:
            with st.expander("📝 Abrir formulário de avaliação", expanded=False):
                with st.spinner("Carregando formulário..."):
                    st.iframe(
                        gerar_url_incorporada(LINK_GOOGLE_FORMS_AVALICAO),
                        height=700,
                    )
                st.caption(
                    "Não carregou? "
                    f"[Abra em uma nova aba]({LINK_GOOGLE_FORMS_AVALICAO})."
                )

    with col_direita:
        st.markdown("### O que a comunidade está dizendo:")
        df_avaliacoes = carregar_com_aviso(URL_RESPOSTAS_AVALIACOES, "Avaliações")

        if not df_avaliacoes.empty:
            nome_col = COL_NOME if COL_NOME in df_avaliacoes.columns else df_avaliacoes.columns[0]
            nota_col = COL_NOTA if COL_NOTA in df_avaliacoes.columns else None
            coment_col = COL_COMENTARIO if COL_COMENTARIO in df_avaliacoes.columns else None

            for _, row in df_avaliacoes.tail(5).iloc[::-1].iterrows():
                nome = row.get(nome_col) or "Anônimo"

                nota_bruta = row.get(nota_col) if nota_col else 5
                try:
                    nota_val = int(float(nota_bruta))
                except (TypeError, ValueError):
                    nota_val = 5
                nota_val = max(1, min(5, nota_val))
                estrelas = "⭐" * nota_val

                comentario = row.get(coment_col) if coment_col else None
                comentario = comentario if pd.notna(comentario) and str(comentario).strip() else "Sem comentários adicionais."

                st.markdown(f"**{nome}** - {estrelas}")
                st.caption(f"\"{comentario}\"")
                st.markdown("---")
        elif not url_e_placeholder(URL_RESPOSTAS_AVALIACOES):
            st.info("Seja o primeiro a avaliar o nosso projeto!")

# ======================================================================================
# AVISO JURÍDICO FIXO NO FINAL DA BARRA LATERAL
# ======================================================================================
st.sidebar.markdown("---")
st.sidebar.caption("**Aviso Legal:**")
st.sidebar.caption(
    "Esta plataforma funciona como um indexador comunitário de livre acesso. "
    "O conteúdo dos links e vídeos externos é de responsabilidade exclusiva de seus "
    "respectivos autores e das plataformas de origem (YouTube, Instagram, etc.)."
)
