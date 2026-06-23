"""Params configuráveis + debug passo a passo (por agente)."""
from jangada_ai import LLM, Flow

# --- Params de geração comuns são first-class ---
llm = LLM(
    "openai", "gpt-4o",
    temperature=0.2,
    max_tokens=800,
    top_p=0.9,
    stop=["\n\n"],
    seed=42,
)
# Trocar pra um modelo que não aceita esses params NÃO quebra:
# em gpt-5 a temperature é descartada e max_tokens vira max_completion_tokens;
# em gemini-3.5 o sampling é descartado. Você não muda nada.

# Override por chamada via params=:
resp = llm.complete("Liste 3 ideias sobre {{x}}", x="corrida", params={"temperature": 0.7})

# --- Debug: liga e vê a cadeia passo a passo, por agente ---
agente = LLM("groq", "llama-3.3-70b-versatile", debug=True, name="resumidor").with_fallback(
    LLM("anthropic", "claude-opus-4-8", name="reserva")
)
agente.complete("Resuma em 1 frase: {{texto}}", texto="...")
# Saída (stderr) mostra: prompt, params, resposta (tempo + tokens) e, se o
# primário falhar, o erro e a troca pro fallback.

# --- Debug por agente dentro de um fluxo ---
rapido = LLM("groq", "llama-3.3-70b-versatile", debug=True, name="rascunhador")
forte = LLM("anthropic", "claude-opus-4-8", debug=True, name="revisor")

flow = (
    Flow(debug=True)  # marca a fronteira de cada passo
    .step("rascunho", "Liste 5 ideias sobre {{tema}}", llm=rapido)
    .step("revisao", "Escolha a melhor e detalhe:\n{{rascunho}}", llm=forte)
)
flow.run(tema="treino de 3km")
# Cada agente (rascunhador, revisor) imprime seu próprio bloco de debug.
