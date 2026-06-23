# Agentes e times

A jangada traz uma camada leve de **orquestração multi-agente** — `Agent` e
`Squad` — construída sobre o que já existe (tool calling, MCP, RAG). Sem
dependência nova: é Python puro compondo a própria lib.

## Agent — um agente com papel e ferramentas

Um `Agent` é um LLM com **papel/objetivo**, opcionalmente com **tools** (funções
que ele executa) e **memória**. Ele roda o loop de tool calling sozinho até a
resposta final.

```python
from jangada_ai import LLM, Agent

def clima(cidade: str) -> str:
    "Retorna o clima de uma cidade."
    return f"ensolarado em {cidade}, 28°C"

meteoro = Agent(
    LLM("openai", "gpt-4o-mini"),
    role="Meteorologista",
    goal="informar o clima de forma clara",
    tools=[clima],
)

res = meteoro.run("Como está o clima em Recife?")
print(res.text)          # o modelo chamou clima("Recife") e respondeu
print(res.cost, res.usage, res.iterations)
```

- `tools=` são **callables** — a função é executada localmente quando o modelo a
  chama, e o resultado volta pro modelo.
- Para um servidor **MCP**, passe `mcp_client=MCPClient(...)` e use **`arun`**
  (async): o agente lista as tools do servidor e as usa junto das suas.

```python
async with MCPClient("https://seu-mcp/mcp/") as mcp:
    agente = Agent(llm, role="Operador", mcp_client=mcp)
    print((await agente.arun("Liste os produtos")).text)
```

## Memória de longo prazo (RAG)

`RAGMemory` dá ao agente memória persistente sobre um `RAG`: antes de responder
ele **recupera** o que é relevante; depois, **guarda** o que aconteceu.

```python
from jangada_ai import LLM, Agent, RAGMemory
from jangada_ai.rag import RAG, InMemoryVectorStore

rag = RAG(LLM("openai", "text-embedding-3-small"), InMemoryVectorStore())
agente = Agent(llm, role="Suporte", memory=RAGMemory(rag, k=3))
```

## Squad — vários agentes colaborando

`Squad` orquestra um time de agentes. Dois processos:

### Sequencial (handoff)

Cada agente roda em ordem e recebe a saída do anterior como contexto:

```python
from jangada_ai import LLM, Agent, Squad

llm = LLM("openai", "gpt-4o-mini")
pesquisador = Agent(llm, role="Pesquisador", goal="levantar fatos")
escritor    = Agent(llm, role="Escritor", goal="escrever um texto claro")

squad = Squad([pesquisador, escritor])
res = squad.run("Escreva um parágrafo sobre jangadas nordestinas.")
print(res.text)            # saída do último agente
print(res.outputs)         # {"Pesquisador": "...", "Escritor": "..."}
```

### Hierárquico (delegação)

Um agente **gerente** recebe ferramentas `delegar_para_<papel>` geradas
automaticamente a partir dos membros e decide a quem delegar cada subtarefa:

```python
gerente = Agent(llm, role="Gerente", goal="coordenar o time")
squad = Squad([pesquisador, escritor], manager=gerente)
res = squad.run("Produza um resumo sobre o tema X.")
```

Tanto `run` quanto `arun` agregam `usage`/`cost` de todo o time.

## Planejamento

`plan()` decompõe um objetivo numa lista ordenada de tarefas (structured output):

```python
from jangada_ai import plan

for tarefa in plan(llm, "Lançar uma newsletter sobre IA", max_tasks=5):
    print("-", tarefa)
```

## Como se relaciona com o resto

Não há mágica nem infra nova: `Agent` é o loop de tool calling (como o
[`run_agent`](mcp.md)); a memória é o [RAG](rag.md); o `Squad` hierárquico usa
delegação por tools ([Tools](tools.md)). Você pode trocar o provider de qualquer
agente sem mudar mais nada — a tese da jangada vale também aqui.
