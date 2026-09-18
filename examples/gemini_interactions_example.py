"""Interactions API e agentes do Gemini (Deep Research).

Requer: pip install "jangada-ai[gemini]"  e  GEMINI_API_KEY no ambiente.
Rode:   python examples/gemini_interactions_example.py
"""
from jangada_ai.interactions import GeminiInteractions

gi = GeminiInteractions(model="gemini-3.8-flash")

# 1) Interação simples com busca do Google (tool nativa) + citações
r = gi.create("Quem venceu a Copa do Mundo de 2002?", tools=[{"type": "google_search"}])
print(r.text)
for c in r.citations:
    print(" -", c["title"], c["url"])

# 2) Continuação stateful (sem reenviar histórico)
r2 = gi.create("E o artilheiro?", previous_interaction_id=r.id)
print(r2.text)


# 3) Function calling com execução local automática
def cotacao(moeda: str) -> float:
    """Cotação da moeda em reais."""
    return {"USD": 5.4, "EUR": 5.9}.get(moeda.upper(), 0.0)


r3 = gi.run("Quanto custam 100 dólares em reais?", tools=[cotacao])
print(r3.text, "| tools:", [t["name"] for t in r3.tool_trace], "| custo:", r3.cost_total)

# 4) Streaming
for ev in gi.stream("Explique RAG em uma frase."):
    if ev.type == "text":
        print(ev.text, end="", flush=True)
print()

# 5) Deep Research (background + polling; leva minutos)
if input("Rodar Deep Research? [s/N] ").strip().lower() == "s":
    rel = gi.deep_research(
        "Panorama do mercado de LLMs open-source em 2026, em 5 tópicos.",
        on_update=lambda x: print("status:", x.status),
    )
    print(rel.text[:2000])
