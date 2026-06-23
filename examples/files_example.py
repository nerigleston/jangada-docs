"""Anexar documentos (docx, pdf, csv, xlsx) a uma chamada.

Por padrão jangada EXTRAI O TEXTO do arquivo localmente e o envia como texto —
barato, funciona em qualquer modelo (não exige vision) e preserva tabelas como
markdown. Vision só é usada para imagens ou quando você força mode='vision'
(ex.: PDF escaneado sem camada de texto).

Requer: pip install 'jangada[files]'   (pypdf, python-docx, openpyxl)
"""
from jangada_ai import LLM, Document

llm = LLM("openai", "gpt-4o-mini")

# 1) Caminho simples: passe os caminhos. O tipo é detectado pela extensão.
#    csv/xlsx/docx/pdf-com-texto -> extração de texto (sem vision).
resp = llm.complete(
    "Resuma os pontos principais destes arquivos.",
    files=["relatorio.pdf", "planilha.xlsx", "contrato.docx"],
)
print(resp.text)

# 2) xlsx com várias abas: todas as abas entram, cada uma rotulada (## Aba: ...).
#    Use max_rows para limitar planilhas gigantes e economizar tokens.
resp = llm.complete(
    "Qual aba tem o maior total?",
    files=[Document("vendas_2026.xlsx", max_rows=200)],
)
print(resp.text)

# 3) Forçar vision (PDF escaneado / quando o layout visual importa):
resp = llm.complete(
    "Transcreva o texto manuscrito.",
    files=[Document("nota_escaneada.pdf", mode="vision")],  # cai para imagem
)
print(resp.text)

# 4) Bytes em memória (upload, fila, etc.) — informe o nome p/ detectar o tipo:
dados = open("export.csv", "rb").read()
resp = llm.complete("Há linhas duplicadas?", files=[Document(dados, name="export.csv")])
print(resp.text)
