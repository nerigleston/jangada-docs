# Tools (function calling)

O modelo pode pedir para chamar **ferramentas** (funções). A API é de **baixo
nível**: o `complete()` devolve as chamadas pedidas em `Completion.tool_calls`,
**você executa** e reenvia o resultado. Suportado em **OpenAI e Groq**
(os outros providers virão).

```python
from jangada_ai import LLM, Message

def get_weather(city: str, units: str = "metric") -> str:
    """Retorna o clima atual de uma cidade."""
    return "25°C, ensolarado"

llm = LLM("openai", "gpt-4o-mini")

# 1) o modelo decide chamar a ferramenta
comp = llm.complete("Como está o tempo em Recife?", tools=[get_weather])

# 2) você executa cada chamada e monta os resultados
results = []
for call in comp.tool_calls:        # call.name, call.args (dict)
    saida = get_weather(**call.args)
    results.append(call.result(saida))

# 3) reenvia: histórico = pergunta + resposta-com-tool-calls + resultados
comp2 = llm.complete(
    "Como está o tempo em Recife?",
    history=[comp.assistant_message(), Message.tool_results(*results)],
    tools=[get_weather],
)
print(comp2.text)
```

## Definindo ferramentas

`tools=[...]` aceita:

- **função Python** — o schema sai da assinatura (type hints) + docstring;
- **modelo Pydantic** — vira o schema dos argumentos;
- **dict** `{"name", "description", "parameters"}` (JSON Schema) já pronto;
- um **`Tool`** (via `to_tool(...)`).

`tool_choice` controla a escolha: `"auto"` (padrão), `"none"`, `"required"`, ou
o **nome** de uma ferramenta para forçá-la.

## Peças

- `Completion.tool_calls`: lista de `ToolCall(id, name, args)`.
- `comp.assistant_message()`: reconstrói a mensagem do assistant (texto + tool
  calls) para o histórico.
- `call.result(saida)`: cria o `ToolResultPart` correspondente.
- `Message.tool_results(*parts)`: empacota os resultados numa mensagem.

## Ferramentas pré-prontas

A jangada traz tools prontas em `jangada_ai.prebuilt`:

```python
from jangada_ai.prebuilt import tavily_search   # busca na web (Tavily)

llm.complete("Qual a cotação do dólar hoje?", tools=[tavily_search])
# execute: tavily_search(**call.args)  (precisa de TAVILY_API_KEY no ambiente)
```

- **`tavily_search`** — busca web em tempo real (Tavily). Chave em
  `TAVILY_API_KEY`, ou `tavily_tool(api_key=...)` para vincular a chave/parâmetros.

Veja também [Structured output](structured-output.md) (que no Anthropic já usa
tool-forcing por baixo) e [Observabilidade](observability.md) (as tool calls
aparecem no trace).
