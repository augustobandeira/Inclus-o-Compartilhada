# Inclusão Compartilhada

Painel Streamlit que indexa atividades pedagógicas inclusivas cadastradas pela comunidade via Google Forms. O app já está **conectado ao Google Forms/Google Planilhas reais** e funcionando com dados ao vivo.

## Arquivos

- `app.py` — aplicação Streamlit (3 abas: Visualizar Atividades, Estatísticas, Avaliar Plataforma).
- `requirements.txt` — dependências (`streamlit`, `pandas`).
- `.streamlit/config.toml` — tema visual (azul acolhedor).

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Com `MODO_TESTE = False` (já configurado), o app carrega as atividades diretamente da planilha real vinculada ao Google Forms. Se a planilha ainda não tiver respostas (ou estiver temporariamente inacessível), o app cai automaticamente nos 24 exemplos embutidos (ver seção abaixo), para nunca ficar "vazio" ou quebrado.

## Exemplos embutidos (dados de demonstração)

`DADOS_EXEMPLO_ATIVIDADES` em `app.py` cobre os 8 tipos de deficiência/neurodivergência do formulário — TEA, TDAH, Deficiência Auditiva, Deficiência Visual, Deficiência Física/Motora, Deficiência Intelectual/Síndrome de Down, Dislexia/Discalculia e Múltiplas deficiências/Outro — com **5 exemplos cada** (1 atividade + 1 artigo originais, 1 exercício didático, e mais 1 atividade + 1 artigo adicionados posteriormente com faixa etária/série diferente), totalizando **40 itens**. Esse conteúdo foi escrito internamente para o projeto (não é conteúdo real de terceiros) e serve para que a plataforma já tenha exemplos de uso completos assim que publicada, mesmo antes de a comunidade enviar suas próprias contribuições pelo formulário. Nenhum desses exemplos tem link de vídeo/conteúdo externo preenchido, para evitar links quebrados ou incorretos.

Cada categoria também tem uma **ilustração** própria (SVG desenhado para o projeto e embutido no código como `data:` URI — sem depender de nenhuma imagem externa), exibida ao lado de cada card na aba "Visualizar Atividades".

A aba "Visualizar Atividades" ganhou um filtro **Tipo de Conteúdo** (Atividade / Artigo / Exercício Didático) e cada card mostra um selo indicando o tipo (🎯 Atividade, 📄 Artigo, ✏️ Exercício Didático). A aba "Estatísticas do Projeto" ganhou um terceiro gráfico com a distribuição por Tipo de Conteúdo.

> O formulário do Google agora também pergunta o Tipo de Conteúdo: a Pergunta 23 ("Tipo de Conteúdo", Múltipla escolha, obrigatória, com as opções Atividade/Artigo/Exercício Didático) foi adicionada como a primeira pergunta da Seção 4, antes de "Título da Atividade". O texto da pergunta bate exatamente com `_COL_TIPO_CONTEUDO` em `app.py`, então a coluna nova na planilha de respostas é reconhecida automaticamente pelo app, sem precisar de nenhum ajuste de código. Respostas antigas (enviadas antes dessa mudança) continuam aparecendo com o selo "🎯 Atividade" por padrão, já que não têm essa coluna preenchida.

### Bug corrigido: "nenhum resultado encontrado" nos filtros (31/08/2026)

Usuários relataram que, ao preencher os filtros de busca (Tipo de Conteúdo, Idade, Série Escolar, Foco/Deficiência), a busca às vezes não retornava nada — mesmo havendo exemplos cadastrados para cada campo isoladamente. Duas causas foram encontradas e corrigidas:

1. **Bug principal:** o filtro de "Foco/Deficiência" usava `.str.contains()` do pandas em modo *regex* (o padrão). Como o nome da categoria **"TEA (Transtorno do Espectro Autista)"** contém parênteses — caracteres especiais de regex — filtrar por essa categoria não encontrava **nenhum resultado, nem os próprios exemplos de TEA**. Corrigido adicionando `regex=False`, para que o texto seja sempre comparado literalmente.
2. **Causa estrutural:** os 4 filtros eram aplicados de forma independente. Como cada categoria tem sua própria combinação fixa de idade/série, era fácil escolher uma combinação de filtros (ex.: Idade "6-8 anos" + Série "1º ano" + Deficiência "Física/Motora") que não existe em nenhuma linha, levando a "nenhum resultado" mesmo com dados válidos. Corrigido tornando os filtros **em cascata**: cada campo agora só oferece as opções que ainda têm pelo menos um resultado dado o que já foi selecionado antes — tornando estruturalmente impossível chegar a uma combinação vazia pela própria interface.

A correção foi verificada com um script de teste (`teste_filtros.py`, incluído no repositório) que simula a lógica antiga e a nova contra os dados reais: a lógica antiga retornava "nenhum resultado" em 84% de todas as combinações de filtros testadas; a lógica nova, 0%.

## Links reais em produção

### Formulário de cadastro de atividades

- **Link para compartilhar/responder:** https://docs.google.com/forms/d/e/1FAIpQLSdB7NQtkg3IP7s314YFxc1mJ5AgPi-vSHsxXvNBqQSNFB5geA/viewform
- **Link de edição (uso interno):** https://docs.google.com/forms/d/1QtXjKZ8tAm1uxYIHOwnlzGZ51QzJSxpRTE86UWQM9AI/edit
- **Planilha de respostas (edição, uso interno):** https://docs.google.com/spreadsheets/d/1l9G_4v5Nbi2_vE23W7TpM6iSrdtSwh_ln8c7WvVv0R4/edit
- **CSV publicado (`URL_RESPOSTAS_ATIVIDADES`):** https://docs.google.com/spreadsheets/d/e/2PACX-1vRjw5AMHEDN0c6o8oczs0btovR0nJyuUyOveNtuydaBYUMr0ztSa3yu1RDNlHmDHsYXn9Q2EnzbVvM1/pub?output=csv

O formulário tem 33 perguntas em 12 seções, com ramificação condicional pela Pergunta 4 ("Para qual tipo de deficiência ou neurodivergência esta atividade foi pensada?") — cada uma das 8 opções leva à seção específica daquele tipo de deficiência/neurodivergência, convergindo depois na seção "Dados gerais da atividade" (que agora começa com a pergunta "Tipo de Conteúdo") e terminando em "Encerramento" (com termo de responsabilidade sobre direitos autorais).

### Formulário de avaliação da plataforma

- **Link para compartilhar/responder:** https://docs.google.com/forms/d/e/1FAIpQLSdRMuq-Yzw8-voPG1iJVPb8xfwOaX0KjbkzCd1GbbANlq253w/viewform
- **Planilha de respostas (edição, uso interno):** https://docs.google.com/spreadsheets/d/1QN0nYkE8tqWAger0gvtUp7Efxsv3XgB33vVlNs2kO0c/edit
- **CSV publicado (`URL_RESPOSTAS_AVALIACOES`):** https://docs.google.com/spreadsheets/d/e/2PACX-1vTNHeeC29SuqocCf1MWM9WciTJU_pKGZIP4l07GBM178_KVisUlz9oRpTA_0E-SzQfW2XBSCEK3DMyv/pub?output=csv

3 perguntas: "Nome" (Resposta curta, opcional), "Nota" (Escala linear 1–5, obrigatória, com marcadores "Muito ruim"/"Excelente") e "Comentário" (Parágrafo, opcional). Os títulos das perguntas foram escolhidos para bater exatamente com os nomes de coluna que `app.py` já esperava ("Nome", "Nota", "Comentário"), então nenhum ajuste de código foi necessário para esta integração.

## O que já está pronto

- Formulário Google criado com título, introdução e as 32 perguntas especificadas em `Formulario_Especificacao_e_Guia_Google_Forms.docx`, incluindo a lógica condicional por tipo de deficiência/neurodivergência.
- Planilha de respostas vinculada e publicada na Web como CSV.
- `app.py` conectado aos links reais (`MODO_TESTE = False`, `URL_RESPOSTAS_ATIVIDADES` e `LINK_GOOGLE_FORMS_CADASTRO` preenchidos).
- **Bug corrigido:** a função `_eh_placeholder()` usava `"google.com" in url` para detectar links não configurados — isso classificava incorretamente *qualquer* link real do Google (Forms/Planilhas, que contêm `docs.google.com`) como um placeholder, fazendo o app sempre cair nos dados de exemplo mesmo com tudo configurado. Corrigido para comparar por igualdade exata contra o placeholder padrão (`https://google.com`), não mais por substring.
- Nomes de colunas do `app.py` ajustados para bater exatamente com o texto das perguntas reais do formulário (ex.: "Título da atividade" com "a" minúsculo, e o texto completo da pergunta de tipo de deficiência), já que a planilha usa o texto literal da pergunta como cabeçalho da coluna.
- Proteção contra planilha real vazia ou fora do ar: se a URL configurada falhar, o app cai automaticamente nos dados de exemplo em vez de mostrar uma tela de erro.
- Segundo formulário — "Avaliação da Plataforma" — criado, publicado e conectado (`LINK_GOOGLE_FORMS_AVALICAO`, `URL_RESPOSTAS_AVALIACOES`). Botões "Compartilhar Nova Atividade" e "Abrir Formulário de Avaliação" ambos ativos, apontando para os formulários reais.
- Testado de ponta a ponta com navegador headless (Playwright): as 3 abas renderizam sem erros, filtros e gráficos funcionam, e o link do botão de cadastro foi verificado apontando para a URL correta.
- Pergunta "Tipo de Conteúdo" adicionada ao formulário de cadastro (Seção 4), para que a comunidade também possa enviar artigos e exercícios didáticos pelo formulário, não só atividades.
- Correção de responsividade no celular: menu lateral agora abre expandido por padrão (`initial_sidebar_state="expanded"`) e o botão de abrir/fechar o menu foi destacado com CSS, para não ficar escondido em navegadores embutidos (ex.: WhatsApp).
- Bug dos filtros de busca corrigido (ver seção acima) e conteúdo de exemplo ampliado de 24 para 40 itens, com uma ilustração própria por categoria de deficiência/neurodivergência.

## Pendências

Nenhuma. Os dois formulários (cadastro de atividades e avaliação da plataforma) estão criados, publicados e conectados ao `app.py`. Todos os botões de call-to-action estão habilitados e apontando para os links reais.

## Publicar de graça no Streamlit Community Cloud

1. Criar uma conta em [github.com](https://github.com) (se ainda não tiver).
2. Criar um repositório novo e enviar `app.py`, `requirements.txt` e a pasta `.streamlit/`.
3. Acessar [share.streamlit.io](https://share.streamlit.io), entrar com o GitHub.
4. Clicar em **New app**, escolher o repositório e definir `app.py` como arquivo principal.
5. Clicar em **Deploy!** — em poucos minutos o link público estará disponível para colocar no relatório da faculdade.

## Aviso jurídico

O rodapé da barra lateral já deixa claro que a plataforma é um indexador comunitário e que o conteúdo dos links externos é de responsabilidade dos respectivos autores — reduzindo o risco jurídico do projeto. O formulário de cadastro também inclui uma declaração de responsabilidade obrigatória sobre direitos autorais na última seção.
