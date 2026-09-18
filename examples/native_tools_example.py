"""Tools NATIVAS: o provider executa (busca, código, leitura de URL) — você só liga.

Rode com uma chave real, ex.:  GEMINI_API_KEY=... python examples/native_tools_example.py
Troque o provider/modelo abaixo (Anthropic, OpenAI) sem mudar o resto.
"""
from jangada_ai import LLM, code_execution, url_context, web_search


def cotacao_interna(moeda: str) -> str:
    "Cotação interna da empresa para uma moeda."
    return "5,10" if moeda.upper() == "USD" else "indisponível"


llm = LLM("gemini", "gemini-3.8-flash")  # ou LLM("anthropic", "claude-sonnet-5") / LLM("openai", "gpt-5")

# 1) busca na web + fontes normalizadas
comp = llm.complete("Qual foi a última decisão do Copom sobre a Selic?", tools=[web_search()])
print(comp.text)
for c in comp.citations:
    print(" -", c.title, c.url)

# 2) execução de código no sandbox do provider
comp = llm.complete("Calcule a soma dos 50 primeiros primos.", tools=[code_execution()])
for call in comp.server_tool_calls:
    print(call.type, call.input, "->", call.output)
print(comp.text)

# 3) tools nativas + function tool na mesma chamada (Gemini 3 / Anthropic / OpenAI)
comp = llm.complete(
    "Compare a cotação do dólar hoje (busque na web) com a nossa cotação interna.",
    tools=[web_search(), cotacao_interna],
)
print(comp.tool_calls or comp.text)

# 4) multi-turn: assistant_message() carrega os blocos nativos de volta
hist = [comp.assistant_message()]
comp = llm.complete("Resuma https://www.bcb.gov.br em 2 linhas.", history=hist, tools=[url_context()])
print(comp.text)
