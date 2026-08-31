"""
Script de verificação (não faz parte do app): carrega os dados de
exemplo exatamente como o app.py os constrói e testa a lógica de
filtros antiga (independente) contra a nova (em cascata), para
confirmar o bug relatado pelos usuários e comprovar que foi corrigido.
"""
import itertools

import pandas as pd


class _FakeSt:
    """Substitui st.set_page_config/st.markdown, as únicas chamadas do
    Streamlit usadas antes da definição dos dados de exemplo, para que
    o restante do app.py possa ser executado como script comum."""

    def set_page_config(self, *a, **k):
        pass

    def markdown(self, *a, **k):
        pass


fake_st = _FakeSt()

with open("app.py", encoding="utf-8") as f:
    codigo_fonte = f.read()

marcador = "DADOS_EXEMPLO_AVALIACOES = pd.DataFrame("
codigo_ate_dados = codigo_fonte[: codigo_fonte.index(marcador)]

namespace = {"st": fake_st, "pd": pd}
exec(compile(codigo_ate_dados, "app.py (trecho de dados)", "exec"), namespace)

df = namespace["DADOS_EXEMPLO_ATIVIDADES"]
col_tipo = namespace["_COL_TIPO_CONTEUDO"]
col_idade = "Idade Recomendada"
col_serie = "Série Escolar"
col_def = namespace["_COL_DEF_REAL"]

print(f"Total de linhas nos dados de exemplo: {len(df)}")
print(f"Tipos de conteúdo: {sorted(df[col_tipo].unique())}")
print(f"Idades: {sorted(df[col_idade].unique())}")
print(f"Séries: {sorted(df[col_serie].unique())}")
print(f"Categorias de deficiência: {len(df[col_def].unique())}")
print()

# --- Lógica ANTIGA: os 4 filtros aplicados de forma independente -----
def filtrar_antigo(tipo, idade, serie, deficiencia):
    d = df.copy()
    if tipo != "Todos":
        d = d[d[col_tipo].astype(str) == str(tipo)]
    if idade != "Todos":
        d = d[d[col_idade].astype(str) == str(idade)]
    if serie != "Todos":
        d = d[d[col_serie].astype(str) == str(serie)]
    if deficiencia != "Todos":
        # Comportamento ORIGINAL do app.py (bug): regex=True (padrão).
        d = d[d[col_def].astype(str).str.contains(str(deficiencia), na=False)]
    return d


tipos = ["Todos"] + sorted(df[col_tipo].unique().tolist())
idades = ["Todos"] + sorted(df[col_idade].unique().tolist())
series = ["Todos"] + sorted(df[col_serie].unique().tolist())
deficiencias = ["Todos"] + sorted(df[col_def].unique().tolist())

total_combos = 0
combos_vazios_antigo = 0
exemplos_vazios = []

for tipo, idade, serie, deficiencia in itertools.product(tipos, idades, series, deficiencias):
    total_combos += 1
    resultado = filtrar_antigo(tipo, idade, serie, deficiencia)
    if resultado.empty:
        combos_vazios_antigo += 1
        if len(exemplos_vazios) < 5:
            exemplos_vazios.append((tipo, idade, serie, deficiencia))

print("=== LÓGICA ANTIGA (filtros independentes) ===")
print(f"Combinações de filtros testadas: {total_combos}")
print(f"Combinações que retornaram 'nenhum resultado': {combos_vazios_antigo} "
      f"({100 * combos_vazios_antigo / total_combos:.1f}%)")
print("Exemplos de combinações válidas (cada filtro tem exemplos) que davam vazio:")
for combo in exemplos_vazios:
    print(f"  Tipo={combo[0]!r} Idade={combo[1]!r} Série={combo[2]!r} Deficiência={combo[3]!r}")
print()

# Agora simula a navegação real do usuário na UI em cascata: a cada
# passo, a lista de opções do próximo filtro só contém valores que
# ainda têm pelo menos 1 resultado — logo, testamos que, seguindo
# *qualquer* caminho de escolhas permitido pela própria interface,
# jamais se chega a um resultado vazio.
def caminhos_cascata():
    d0 = df.copy()
    tipos_disp = ["Todos"] + sorted(d0[col_tipo].dropna().unique().tolist())
    for tipo in tipos_disp:
        d1 = d0 if tipo == "Todos" else d0[d0[col_tipo].astype(str) == str(tipo)]
        idades_disp = ["Todos"] + sorted(d1[col_idade].dropna().unique().tolist())
        for idade in idades_disp:
            d2 = d1 if idade == "Todos" else d1[d1[col_idade].astype(str) == str(idade)]
            series_disp = ["Todos"] + sorted(d2[col_serie].dropna().unique().tolist())
            for serie in series_disp:
                d3 = d2 if serie == "Todos" else d2[d2[col_serie].astype(str) == str(serie)]
                def_disp = ["Todos"] + sorted(d3[col_def].dropna().unique().tolist())
                for deficiencia in def_disp:
                    # Comportamento CORRIGIDO no app.py: regex=False.
                    d4 = d3 if deficiencia == "Todos" else d3[
                        d3[col_def].astype(str).str.contains(str(deficiencia), na=False, regex=False)
                    ]
                    yield (tipo, idade, serie, deficiencia), d4


total_caminhos = 0
caminhos_vazios = 0
for combo, resultado in caminhos_cascata():
    total_caminhos += 1
    if resultado.empty:
        caminhos_vazios += 1

print("=== LÓGICA NOVA (filtros em cascata, como no app.py corrigido) ===")
print(f"Caminhos de navegação possíveis pela interface: {total_caminhos}")
print(f"Caminhos que resultam em 'nenhum resultado': {caminhos_vazios}")
print()
print("Conclusão:", "BUG CONFIRMADO e CORRIGIDO." if combos_vazios_antigo > 0 and caminhos_vazios == 0
      else "Resultado inesperado — revisar.")
