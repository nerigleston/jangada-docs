"""Tool/function calling (baixo nível) + ferramenta pré-pronta (Tavily).

Suportado em OpenAI e Groq. O modelo pede a chamada; você executa e reenvia.
"""
import os

from jangada_ai import LLM, Message
from jangada_ai.prebuilt import tavily_search


def get_weather(city: str, units: str = "metric") -> str:
    """Retorna o clima atual de uma cidade."""
    return f"{city}: 25°C, ensolarado"


llm = LLM("openai", "gpt-4o-mini")

# --- ferramenta própria ---
pergunta = "Como está o tempo em Recife agora?"
comp = llm.complete(pergunta, tools=[get_weather])

if comp.tool_calls:
    results = [call.result(get_weather(**call.args)) for call in comp.tool_calls]
    final = llm.complete(
        pergunta,
        history=[comp.assistant_message(), Message.tool_results(*results)],
        tools=[get_weather],
    )
    print(final.text)

# --- ferramenta pré-pronta: busca na web (precisa de TAVILY_API_KEY) ---
if os.environ.get("TAVILY_API_KEY"):
    pergunta = "Qual a notícia mais recente sobre a Anthropic?"
    comp = llm.complete(pergunta, tools=[tavily_search])
    if comp.tool_calls:
        results = [call.result(tavily_search(**call.args)) for call in comp.tool_calls]
        final = llm.complete(
            pergunta,
            history=[comp.assistant_message(), Message.tool_results(*results)],
            tools=[tavily_search],
        )
        print(final.text)
