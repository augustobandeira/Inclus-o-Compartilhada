# -*- coding: utf-8 -*-
"""
Gera os PDFs completos da "Biblioteca de Materiais" a partir do conteúdo
estruturado abaixo. Não faz parte do app.py (roda uma única vez para
produzir os arquivos em materiais/); o app apenas lê os PDFs já gerados.

Uso:
    python3 gerar_biblioteca.py
"""
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable,
)

PASTA_SAIDA = os.path.dirname(os.path.abspath(__file__))

styles = getSampleStyleSheet()
estilo_titulo = ParagraphStyle(
    "TituloArtigo", parent=styles["Title"], fontSize=18, leading=22,
    textColor="#2F4030", spaceAfter=4,
)
estilo_categoria = ParagraphStyle(
    "Categoria", parent=styles["Normal"], fontSize=11, textColor="#4F6F52",
    spaceAfter=14, fontName="Helvetica-Bold",
)
estilo_secao = ParagraphStyle(
    "Secao", parent=styles["Heading2"], fontSize=13, textColor="#2F4030",
    spaceBefore=14, spaceAfter=6,
)
estilo_corpo = ParagraphStyle(
    "Corpo", parent=styles["Normal"], fontSize=10.5, leading=15,
    alignment=TA_JUSTIFY, spaceAfter=8,
)
estilo_item = ParagraphStyle(
    "Item", parent=estilo_corpo, spaceAfter=4,
)
estilo_referencia = ParagraphStyle(
    "Referencia", parent=styles["Normal"], fontSize=8.5, leading=12,
    textColor="#555555", spaceAfter=4,
)
estilo_rodape = ParagraphStyle(
    "Rodape", parent=styles["Normal"], fontSize=8, textColor="#888888",
    spaceBefore=16,
)


def construir_pdf(slug, titulo, categoria, secoes, referencias):
    caminho = os.path.join(PASTA_SAIDA, f"{slug}.pdf")
    doc = SimpleDocTemplate(
        caminho, pagesize=A4,
        topMargin=2.2 * cm, bottomMargin=2.2 * cm,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        title=titulo, author="Inclusão Compartilhada",
    )
    partes = [
        Paragraph(titulo, estilo_titulo),
        Paragraph(f"Categoria: {categoria} — Biblioteca Inclusão Compartilhada", estilo_categoria),
        HRFlowable(width="100%", color="#4F6F52", thickness=1),
        Spacer(1, 10),
    ]
    for nome_secao, conteudo in secoes:
        partes.append(Paragraph(nome_secao, estilo_secao))
        eh_lista_topicos = bool(conteudo) and all(
            isinstance(c, str) and c.startswith("• ") for c in conteudo
        )
        if eh_lista_topicos:
            # lista de tópicos
            itens = [ListItem(Paragraph(c[2:], estilo_item), leftIndent=6) for c in conteudo]
            partes.append(ListFlowable(itens, bulletType="bullet", start="circle", leftIndent=14))
        else:
            for paragrafo in conteudo:
                partes.append(Paragraph(paragrafo, estilo_corpo))

    partes.append(Spacer(1, 10))
    partes.append(HRFlowable(width="100%", color="#CCCCCC", thickness=0.7))
    partes.append(Paragraph("Referências", estilo_secao))
    for ref in referencias:
        partes.append(Paragraph(ref, estilo_referencia))

    partes.append(Paragraph(
        "Material produzido para a Biblioteca da plataforma Inclusão Compartilhada "
        "(projeto de extensão universitária). Não substitui avaliação ou "
        "acompanhamento individualizado por profissionais especializados.",
        estilo_rodape,
    ))

    doc.build(partes)
    print(f"Gerado: {caminho}")


ARTIGOS = [
    dict(
        slug="tea",
        titulo="Adaptando Atividades Pedagógicas para Estudantes com TEA",
        categoria="TEA (Transtorno do Espectro Autista)",
        secoes=[
            ("1. Contexto", [
                "O Transtorno do Espectro Autista (TEA) é uma condição do neurodesenvolvimento "
                "caracterizada por diferenças na comunicação e na interação social, associadas a "
                "padrões restritos e repetitivos de comportamento, interesse ou atividade. A "
                "palavra \"espectro\" indica que essas características se manifestam de forma muito "
                "variável de pessoa para pessoa, tanto em intensidade quanto em combinação.",
                "No Brasil, a Lei nº 12.764/2012 institui a Política Nacional de Proteção dos "
                "Direitos da Pessoa com Transtorno do Espectro Autista e, em seu art. 1º, § 2º, "
                "estabelece que a pessoa com TEA é considerada pessoa com deficiência para todos os "
                "efeitos legais — o que garante, entre outros direitos, acesso à educação comum e "
                "ao Atendimento Educacional Especializado (AEE).",
            ]),
            ("2. Princípios de adaptação (Desenho Universal para Aprendizagem)", [
                "Representação: oferecer apoios visuais (agenda do dia, pictogramas, histórias "
                "sociais) e reduzir estímulos ambíguos ou excessivos no ambiente.",
                "Ação e expressão: aceitar diferentes formas de resposta — fala, Comunicação "
                "Alternativa (CAA), escrita, apontar — sem exigir sempre a mesma via de expressão.",
                "Engajamento: manter rotinas previsíveis, antecipar mudanças com antecedência e "
                "usar os interesses específicos do aluno como ponte para novos conteúdos.",
            ]),
            ("3. Estratégias práticas em sala de aula", [
                "• Montar uma rotina visual do dia, com cartões ou pictogramas que possam ser "
                "movidos conforme cada etapa é concluída.",
                "• Antecipar verbalmente e visualmente qualquer mudança na rotina habitual.",
                "• Regular o ambiente sensorial: iluminação, ruído e cheiros intensos podem gerar "
                "desconforto significativo.",
                "• Planejar pausas estruturadas em momentos de transição ou sobrecarga sensorial.",
                "• Usar histórias sociais para preparar o aluno para situações novas (uma excursão, "
                "uma avaliação, uma mudança de professor).",
                "• Explorar os interesses restritos do aluno (um tema, um personagem) como porta de "
                "entrada para atividades de leitura, escrita ou matemática.",
            ]),
            ("4. Papel da família e do AEE", [
                "O Plano Educacional Individualizado (PEI), construído em conjunto com a família e "
                "a equipe do AEE, ajuda a alinhar expectativas e estratégias entre a escola e a "
                "casa. A comunicação constante entre professor regente, AEE e família é o que "
                "sustenta a coerência das adaptações ao longo do tempo.",
            ]),
        ],
        referencias=[
            "BRASIL. Lei nº 12.764, de 27 de dezembro de 2012. Institui a Política Nacional de "
            "Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista. Diário Oficial da "
            "União, Brasília, DF, 28 dez. 2012.",
            "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com "
            "Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.",
            "BRASIL. Ministério da Educação. Base Nacional Comum Curricular. Brasília: MEC, 2018.",
            "CAST. Universal Design for Learning Guidelines, version 3.0. Lynnfield, MA: CAST, 2024.",
        ],
    ),
    dict(
        slug="tdah",
        titulo="Estratégias de Apoio para Estudantes com TDAH em Sala de Aula",
        categoria="TDAH",
        secoes=[
            ("1. Contexto", [
                "O Transtorno de Déficit de Atenção/Hiperatividade (TDAH) é um transtorno do "
                "neurodesenvolvimento caracterizado por um padrão persistente de desatenção e/ou "
                "hiperatividade-impulsividade que interfere no funcionamento e no desenvolvimento — "
                "não se trata de falta de esforço, disciplina ou vontade do estudante.",
                "A Lei nº 14.254, de 30 de novembro de 2021, institui a Política Nacional de "
                "Acompanhamento Integral do Educando com Dislexia, Transtorno do Déficit de Atenção "
                "com Hiperatividade (TDAH) e outros Transtornos de Aprendizagem, determinando que as "
                "redes de ensino ofereçam acompanhamento e capacitem seus profissionais para "
                "identificar sinais desses transtornos.",
            ]),
            ("2. Princípios de adaptação (Desenho Universal para Aprendizagem)", [
                "Engajamento: dividir tarefas longas em blocos curtos e variados, intercalados com "
                "pausas ativas programadas.",
                "Ação e expressão: permitir movimento controlado durante a atividade e aceitar "
                "respostas em formatos diferentes (oral, escrito, esquema visual).",
                "Representação: instruções curtas e diretas, reforçadas por checklists visuais em "
                "vez de comandos verbais longos.",
            ]),
            ("3. Estratégias práticas em sala de aula", [
                "• Dividir tarefas longas em etapas menores, com metas claras para cada bloco.",
                "• Usar cronômetros visuais (ampulheta, disco colorido) para tornar a passagem do "
                "tempo perceptível.",
                "• Programar pausas ativas de 2 a 5 minutos entre blocos de concentração.",
                "• Combinar comandos verbais com apoio visual (agenda na carteira, lista de tarefas "
                "ilustrada).",
                "• Priorizar o assento em local com menos distrações visuais e sonoras.",
                "• Dar retorno (feedback) imediato e específico, reforçando avanços pequenos.",
            ]),
            ("4. Papel da família e do AEE", [
                "O acompanhamento integral previsto na Lei nº 14.254/2021 pressupõe articulação "
                "entre escola, família e, quando houver, profissionais de saúde envolvidos no "
                "cuidado do estudante. O PEI, quando necessário, documenta as adaptações combinadas "
                "entre essas partes.",
            ]),
        ],
        referencias=[
            "BRASIL. Lei nº 14.254, de 30 de novembro de 2021. Institui a Política Nacional de "
            "Acompanhamento Integral do Educando com Dislexia, Transtorno do Déficit de Atenção com "
            "Hiperatividade (TDAH) e outros Transtornos de Aprendizagem. Diário Oficial da União, "
            "Brasília, DF, 1 dez. 2021.",
            "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com "
            "Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.",
            "CAST. Universal Design for Learning Guidelines, version 3.0. Lynnfield, MA: CAST, 2024.",
        ],
    ),
    dict(
        slug="deficiencia-auditiva",
        titulo="Inclusão de Estudantes Surdos e com Deficiência Auditiva",
        categoria="Deficiência Auditiva",
        secoes=[
            ("1. Contexto", [
                "A Língua Brasileira de Sinais (Libras) é reconhecida como meio legal de comunicação "
                "e expressão da comunidade surda brasileira pela Lei nº 10.436, de 24 de abril de "
                "2002, regulamentada pelo Decreto nº 5.626, de 22 de dezembro de 2005. Esse decreto "
                "estabelece as bases para uma educação bilíngue, em que a Libras é a primeira língua "
                "e o português escrito, a segunda.",
                "Nem toda pessoa com deficiência auditiva é usuária de Libras — há também estudantes "
                "oralizados, com implante coclear ou aparelho auditivo, cada um com necessidades de "
                "apoio distintas.",
            ]),
            ("2. Princípios de adaptação (Desenho Universal para Aprendizagem)", [
                "Representação: combinar Libras, legendas e apoio visual forte em todo material "
                "apresentado.",
                "Ação e expressão: aceitar respostas em Libras, escrita ou oralidade, conforme o "
                "perfil do estudante.",
                "Engajamento: materiais visualmente ricos e contextualizados, já que grande parte "
                "da informação em sala é veiculada por via auditiva.",
            ]),
            ("3. Estratégias práticas em sala de aula", [
                "• Garantir contato visual e estar de frente para o estudante antes de começar a "
                "falar.",
                "• Contar com intérprete ou apoio em Libras nas atividades quando o estudante for "
                "usuário dessa língua.",
                "• Usar vídeos com legenda em português e, quando possível, janela de intérprete.",
                "• Reforçar instruções orais com registro escrito ou visual no quadro.",
                "• Ensinar noções básicas de Libras para toda a turma, favorecendo a interação "
                "social e não apenas a comunicação pedagógica.",
            ]),
            ("4. Papel da família e do AEE", [
                "O AEE em Libras e em Língua Portuguesa (na modalidade escrita) funciona como "
                "complemento à sala comum, nunca como substituto. A continuidade do uso da Libras "
                "em casa, quando a família também aprende a língua, fortalece o desenvolvimento "
                "linguístico do estudante.",
            ]),
        ],
        referencias=[
            "BRASIL. Lei nº 10.436, de 24 de abril de 2002. Dispõe sobre a Língua Brasileira de "
            "Sinais - Libras. Diário Oficial da União, Brasília, DF, 25 abr. 2002.",
            "BRASIL. Decreto nº 5.626, de 22 de dezembro de 2005. Regulamenta a Lei nº 10.436/2002. "
            "Diário Oficial da União, Brasília, DF, 23 dez. 2005.",
            "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com "
            "Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.",
        ],
    ),
    dict(
        slug="deficiencia-visual",
        titulo="Materiais Acessíveis para Estudantes com Deficiência Visual",
        categoria="Deficiência Visual",
        secoes=[
            ("1. Contexto", [
                "A deficiência visual abrange desde a baixa visão até a cegueira total, exigindo "
                "que o conteúdo pedagógico seja disponibilizado por canais sensoriais "
                "complementares — principalmente o tato e a audição — e com o apoio de tecnologia "
                "assistiva, como leitores de tela e materiais em Braille.",
            ]),
            ("2. Princípios de adaptação (Desenho Universal para Aprendizagem)", [
                "Representação: oferecer versões táteis, sonoras ou com audiodescrição de qualquer "
                "material visual.",
                "Ação e expressão: aceitar respostas orais, em Braille ou por softwares de leitura "
                "e escrita.",
                "Engajamento: priorizar materiais manipuláveis e experiências concretas sempre que "
                "possível.",
            ]),
            ("3. Estratégias práticas em sala de aula", [
                "• Descrever em voz alta imagens, gráficos e vídeos apresentados em aula "
                "(audiodescrição).",
                "• Produzir ou adaptar materiais em relevo ou Braille para conceitos geométricos, "
                "mapas e diagramas.",
                "• Manter a organização física da sala estável, avisando o estudante sobre qualquer "
                "mudança de layout.",
                "• Disponibilizar textos em formato compatível com leitores de tela com antecedência.",
                "• Trabalhar orientação e mobilidade em parceria com o profissional especializado, "
                "quando disponível.",
            ]),
            ("4. Papel da família e do AEE", [
                "O AEE oferece apoio em Braille, no uso do soroban, de tecnologia assistiva e de "
                "orientação e mobilidade. A antecedência na produção de materiais adaptados — "
                "avisada pela família ou pelo próprio AEE — é determinante para que o estudante "
                "acompanhe a turma no mesmo ritmo.",
            ]),
        ],
        referencias=[
            "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com "
            "Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.",
            "BRASIL. Ministério da Educação. Secretaria de Educação Especial. Política Nacional de "
            "Educação Especial na Perspectiva da Educação Inclusiva. Brasília: MEC/SEESP, 2008.",
            "CAST. Universal Design for Learning Guidelines, version 3.0. Lynnfield, MA: CAST, 2024.",
        ],
    ),
    dict(
        slug="deficiencia-fisica-motora",
        titulo="Acessibilidade e Adaptações para Estudantes com Deficiência Física/Motora",
        categoria="Deficiência Física/Motora",
        secoes=[
            ("1. Contexto", [
                "A deficiência física ou motora abrange limitações de mobilidade, força ou "
                "coordenação, de diferentes origens e graus. A resposta pedagógica passa tanto pela "
                "acessibilidade do ambiente físico quanto pela adaptação dos materiais usados em "
                "sala de aula.",
            ]),
            ("2. Princípios de adaptação (Desenho Universal para Aprendizagem)", [
                "Ação e expressão: oferecer formas alternativas de manipular materiais e de "
                "registrar respostas (oral, digital, com apoio de terceiros).",
                "Representação: posicionar materiais ao alcance visual e físico do estudante.",
                "Engajamento: ajustar o nível de esforço motor exigido por cada atividade ao perfil "
                "de cada aluno, sem excluí-lo da proposta coletiva.",
            ]),
            ("3. Estratégias práticas em sala de aula", [
                "• Adaptar materiais escolares com engrossadores de lápis, apoios de mesa ou "
                "pranchas inclinadas.",
                "• Garantir rotas e mobiliário acessíveis, seguindo os parâmetros da norma técnica "
                "NBR 9050 da ABNT.",
                "• Oferecer tempo adicional para atividades que exijam esforço motor mais intenso.",
                "• Usar tecnologia assistiva (teclados adaptados, softwares de acesso por switch) "
                "quando indicada.",
                "• Adaptar jogos e atividades físicas em vez de dispensar o estudante delas — por "
                "exemplo, ajustando distância, altura ou peso dos materiais.",
            ]),
            ("4. Papel da família e do AEE", [
                "Quando o estudante é acompanhado por fisioterapia ou terapia ocupacional, o diálogo "
                "entre esses profissionais, a família e o AEE ajuda a alinhar as adaptações da sala "
                "de aula com o restante do plano terapêutico.",
            ]),
        ],
        referencias=[
            "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com "
            "Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.",
            "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. NBR 9050: Acessibilidade a edificações, "
            "mobiliário, espaços e equipamentos urbanos. Rio de Janeiro: ABNT.",
            "BRASIL. Ministério da Educação. Base Nacional Comum Curricular. Brasília: MEC, 2018.",
        ],
    ),
    dict(
        slug="deficiencia-intelectual-down",
        titulo="Ensino Estruturado para Estudantes com Deficiência Intelectual e Síndrome de Down",
        categoria="Deficiência Intelectual / Síndrome de Down",
        secoes=[
            ("1. Contexto", [
                "A deficiência intelectual caracteriza-se por limitações significativas tanto no "
                "funcionamento intelectual quanto no comportamento adaptativo. A Síndrome de Down é "
                "uma das causas genéticas mais conhecidas de deficiência intelectual, mas é "
                "importante lembrar que nem toda deficiência intelectual está associada a ela — e "
                "que o potencial de aprendizagem varia muito de pessoa para pessoa.",
            ]),
            ("2. Princípios de adaptação (Desenho Universal para Aprendizagem)", [
                "Representação: usar linguagem simples e direta, com apoio visual constante e, "
                "quando necessário, Comunicação Alternativa e Aumentativa (CAA).",
                "Ação e expressão: aceitar múltiplas formas de o estudante demonstrar o que "
                "aprendeu, além da escrita convencional.",
                "Engajamento: propor etapas pequenas e alcançáveis, celebrando cada conquista para "
                "sustentar a motivação.",
            ]),
            ("3. Estratégias práticas em sala de aula", [
                "• Usar cartões de CAA para mediar comunicação, pedidos e escolhas do dia a dia.",
                "• Dividir conteúdos complexos em passos pequenos e concretos.",
                "• Adotar currículo funcional quando indicado pela equipe pedagógica, sem abrir mão "
                "de altas expectativas de aprendizagem.",
                "• Repetir atividades com pequenas variações, reforçando a consolidação sem tornar a "
                "tarefa repetitiva demais.",
                "• Celebrar publicamente pequenas conquistas, fortalecendo a autoestima e o "
                "engajamento.",
            ]),
            ("4. Papel da família e do AEE", [
                "O PEI construído em conjunto com a família orienta as prioridades de cada etapa. O "
                "AEE apoia na introdução e no uso consistente de CAA entre a escola e a casa, o que "
                "é determinante para sua eficácia.",
            ]),
        ],
        referencias=[
            "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com "
            "Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.",
            "BRASIL. Ministério da Educação. Secretaria de Educação Especial. Política Nacional de "
            "Educação Especial na Perspectiva da Educação Inclusiva. Brasília: MEC/SEESP, 2008.",
            "CAST. Universal Design for Learning Guidelines, version 3.0. Lynnfield, MA: CAST, 2024.",
        ],
    ),
    dict(
        slug="dislexia-discalculia",
        titulo="Apoio Pedagógico para Dislexia e Discalculia",
        categoria="Dislexia / Discalculia",
        secoes=[
            ("1. Contexto", [
                "Dislexia e discalculia são Transtornos Específicos de Aprendizagem: a primeira "
                "afeta principalmente a leitura e a escrita, a segunda, o raciocínio matemático. "
                "Nenhuma das duas está relacionada ao nível de inteligência do estudante — são "
                "diferenças no processamento de informação específicas para essas áreas.",
                "A Lei nº 14.254/2021 garante acompanhamento integral também a esses estudantes, "
                "determinando que as redes de ensino capacitem seus profissionais para identificar "
                "sinais de alerta o quanto antes.",
            ]),
            ("2. Princípios de adaptação (Desenho Universal para Aprendizagem)", [
                "Representação: usar fonte, espaçamento e contraste adequados, além de material "
                "multissensorial (visual, auditivo, tátil).",
                "Ação e expressão: oferecer tempo adicional e, quando pertinente, avaliação oral "
                "como alternativa à escrita.",
                "Engajamento: usar jogos e material concreto para tornar a prática menos "
                "repetitiva e mais motivadora.",
            ]),
            ("3. Estratégias práticas em sala de aula", [
                "• Adotar método multissensorial (visual + auditivo + tátil) no ensino da leitura.",
                "• Usar material concreto para matemática, como reta numérica manipulável e material "
                "dourado.",
                "• Conceder tempo adicional para leitura, escrita e resolução de exercícios.",
                "• Praticar leitura compartilhada em voz alta, com apoio de áudio quando disponível.",
                "• Permitir uso de calculadora ou tabelas de apoio em discalculia, quando a avaliação "
                "não tiver como foco o cálculo mental em si.",
            ]),
            ("4. Papel da família e do AEE", [
                "A identificação precoce, seguida do encaminhamento adequado, é o fator que mais "
                "influencia o sucesso das intervenções. A Lei nº 14.254/2021 reforça que esse "
                "acompanhamento deve ser contínuo, e não pontual, ao longo da trajetória escolar.",
            ]),
        ],
        referencias=[
            "BRASIL. Lei nº 14.254, de 30 de novembro de 2021. Institui a Política Nacional de "
            "Acompanhamento Integral do Educando com Dislexia, TDAH e outros Transtornos de "
            "Aprendizagem. Diário Oficial da União, Brasília, DF, 1 dez. 2021.",
            "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com "
            "Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.",
        ],
    ),
    dict(
        slug="multiplas-deficiencias",
        titulo="Planejamento Individualizado para Múltiplas Deficiências e Outras Condições",
        categoria="Múltiplas deficiências / Outro",
        secoes=[
            ("1. Contexto", [
                "Quando um estudante apresenta mais de uma condição associada — por exemplo, "
                "deficiência física e deficiência visual — ou uma condição que não se encaixa nas "
                "categorias mais comuns, a resposta pedagógica precisa ser necessariamente "
                "individualizada, combinando estratégias de diferentes áreas em vez de aplicar uma "
                "receita única.",
            ]),
            ("2. Princípios de adaptação (Desenho Universal para Aprendizagem)", [
                "Representação e ação/expressão: combinar os apoios relevantes para cada condição "
                "envolvida, priorizando sempre a comunicação como base de qualquer adaptação.",
                "Engajamento: construir o plano em conjunto com a equipe multidisciplinar e a "
                "família, revisando-o com regularidade conforme o estudante se desenvolve.",
            ]),
            ("3. Estratégias práticas em sala de aula", [
                "• Partir de uma avaliação multidisciplinar para identificar quais adaptações têm "
                "maior impacto.",
                "• Priorizar a comunicação alternativa como ponto de partida quando houver limitação "
                "de fala.",
                "• Combinar estratégias de diferentes áreas (visual, motora, de comunicação) em vez "
                "de escolher apenas uma.",
                "• Registrar em uma ficha simples quais adaptações estão em uso, para consulta "
                "rápida por qualquer professor que atenda o estudante.",
            ]),
            ("4. Papel da família e do AEE", [
                "O Plano Educacional Individualizado (PEI) é especialmente importante nesses casos, "
                "reunindo em um único documento as orientações da equipe multidisciplinar, da "
                "família e do AEE — e deve ser revisado periodicamente, à medida que o estudante "
                "avança.",
            ]),
        ],
        referencias=[
            "BRASIL. Lei nº 13.146, de 6 de julho de 2015. Lei Brasileira de Inclusão da Pessoa com "
            "Deficiência. Diário Oficial da União, Brasília, DF, 7 jul. 2015.",
            "BRASIL. Ministério da Educação. Secretaria de Educação Especial. Política Nacional de "
            "Educação Especial na Perspectiva da Educação Inclusiva. Brasília: MEC/SEESP, 2008.",
            "CAST. Universal Design for Learning Guidelines, version 3.0. Lynnfield, MA: CAST, 2024.",
        ],
    ),
]


if __name__ == "__main__":
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    for artigo in ARTIGOS:
        construir_pdf(
            artigo["slug"], artigo["titulo"], artigo["categoria"],
            artigo["secoes"], artigo["referencias"],
        )
    print(f"\n{len(ARTIGOS)} PDFs gerados em {PASTA_SAIDA}")
