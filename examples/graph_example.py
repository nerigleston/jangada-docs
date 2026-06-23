"""Orquestração: roteamento condicional e execução paralela de agentes."""
import asyncio

from jangada_ai import LLM, Graph

triagem = LLM("groq", "llama-3.3-70b-versatile", name="triagem")
tecnico = LLM("anthropic", "claude-opus-4-8", name="tecnico")
geral = LLM("gemini", "gemini-2.5-flash", name="geral")

# --- 1) Roteamento condicional: 1 agente roda antes e decide o próximo ---
g = Graph(debug=True)
g.node("triagem", triagem, "Responda só com 'tecnico' ou 'geral': {{pergunta}}")
g.node("tecnico", tecnico, "Responda tecnicamente: {{pergunta}}")
g.node("geral", geral, "Responda de forma simples: {{pergunta}}")
g.route("triagem", lambda ctx: "tecnico" if "tecnico" in ctx["triagem"].lower() else "geral")

resultado = g.run("triagem", pergunta="como funciona o handshake TCP?")
print(resultado.path)          # ex.: ['triagem', 'tecnico']
print(resultado.last if False else resultado[resultado.path[-1]])

# --- 2) Paralelo: dois agentes ao mesmo tempo, depois uma síntese ---
pa = LLM("groq", "llama-3.3-70b-versatile", name="pesq_mercado")
pb = LLM("gemini", "gemini-2.5-flash", name="pesq_tecnica")
sintese = LLM("anthropic", "claude-opus-4-8", name="sintese")

g2 = Graph()
g2.parallel(
    "pesquisas",
    {
        "mercado": (pa, "Analise o mercado de: {{tema}}"),
        "tecnica": (pb, "Analise a viabilidade técnica de: {{tema}}"),
    },
    join="sintese",
)
g2.node("sintese", sintese, "Combine as análises:\nMercado: {{mercado}}\nTécnica: {{tecnica}}")

r2 = g2.run("pesquisas", tema="app de corrida com IA")
print(r2["sintese"])

# --- 3) Vice-versa: rotear PARA um bloco paralelo, e em FastAPI usar arun ---
async def main():
    g3 = Graph()
    g3.node("decisor", triagem, "Vale aprofundar? responda 'sim'/'nao': {{q}}")
    g3.parallel("aprofundar", {"a": (pa, "Ângulo A: {{q}}"), "b": (pb, "Ângulo B: {{q}}")})
    g3.route("decisor", lambda ctx: "aprofundar" if "sim" in ctx["decisor"].lower() else None)
    return await g3.arun("decisor", q="devo migrar pro Kubernetes?")

# asyncio.run(main())
