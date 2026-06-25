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
  chama, e o resultado volta pro modelo. Podem ser **síncronas** (`def`) ou
  **assíncronas** (`async def`): tools `async def` são aguardadas no laço de
  `arun`. No `run` (síncrono) só use tools síncronas — uma tool async vira um
  resultado de erro orientando a usar `arun`.
- Para um servidor **MCP**, passe `mcp_client=MCPClient(...)` e use **`arun`**
  (async): o agente lista as tools do servidor e as usa junto das suas.

```python
async with MCPClient("https://seu-mcp/mcp/") as mcp:
    agente = Agent(llm, role="Operador", mcp_client=mcp)
    print((await agente.arun("Liste os produtos")).text)
```

## Conversa multi-turno (`history=`)

`run`/`arun` aceitam um `history` de turnos anteriores (`list[Message]`) — eles
entram **antes** da nova tarefa, dando continuidade fiel ao diálogo. O
`AgentResult.messages` devolve o histórico completo daquele turno, que você pode
**persistir** (ex.: numa tabela por `conversation_id`) e reinjetar no próximo:

```python
from jangada_ai.message import Message

historico = [
    Message("user", "Quanto gastei em maio?"),
    Message("assistant", "R$ 3.200 em maio."),
]
res = await agente.arun("E no mês anterior?", history=historico)
# guarde res.messages (ou só os pares user/assistant) para o próximo turno
```

> Diferente de um *checkpointer* que serializa o estado inteiro do grafo, aqui o
> histórico é **explícito**: você decide o que persistir e reinjetar. Para
> recall semântico (e não turn-by-turn), use `RAGMemory` (abaixo) — os dois
> compõem.

## Streaming da resposta (`astream`)

`astream` emite a **resposta final** token-a-token. As tool-calls (function tools
e MCP) são resolvidas internamente antes — o protocolo de stream não expõe
`tool_calls`, então não há streaming *durante* a fase de ferramentas; quando o
agente chega à resposta final, ela sai incremental. Sem tools, streama direto.

```python
async for token in agente.astream("Resuma meus gastos do mês"):
    print(token, end="", flush=True)
```

## Agent Card (descoberta / A2A)

`card()` devolve metadados descobríveis do agente no vocabulário do **Agent Card**
do protocolo [A2A](https://a2a-protocol.org) (`name`, `description`, `version`,
`url`, `capabilities`, `skills`):

```python
sofia = Agent(llm, role="Sofia", goal="assistente financeira", tools=[buscar])
sofia.card(url="https://app.exemplo/agents/sofia", version="1.0.0")
# {"name": "Sofia", "capabilities": {"streaming": True, ...},
#  "skills": [{"id": "buscar", "description": "...", "parameters": {...}}], ...}
```

## Servidor A2A (transporte HTTP/JSON-RPC) — `jangada[a2a]`

O extra `jangada[a2a]` expõe um (ou vários) `Agent` como um **servidor A2A** de
verdade, falando o binding JSON-RPC do protocolo: descoberta do Agent Card,
`message/send` (síncrono) e `message/stream` (SSE), com **continuidade por
`contextId`** (o histórico de cada conversa é mantido e reinjetado).

```python
from jangada_ai import LLM, Agent
from jangada_ai.a2a import A2AHandler, build_a2a_app

sofia = Agent(LLM("openai", "gpt-4o-mini"), role="Sofia", goal="finanças", tools=[buscar])
app = build_a2a_app(A2AHandler(sofia, url="https://app.exemplo/a2a"))
# app é um ASGI Starlette — sirva com uvicorn:  uvicorn modulo:app
```

Rotas servidas:

| Rota | O quê |
|------|-------|
| `GET /.well-known/agent.json` | Agent Card do agente principal |
| `GET /agents` | catálogo (lista de Agent Cards) |
| `POST /` | JSON-RPC `message/send` (JSON), `message/stream` (SSE), `tasks/get`, `tasks/cancel` |
| `POST /agents/{name}` | idem, para um agente específico do catálogo |

Para um time descobrível, passe uma lista: `build_a2a_app([sofia_h, orcamento_h])`.
A **lógica do protocolo** vive em `A2AHandler` (Python puro, testável sem rede); o
servidor ASGI importa Starlette só aqui. O histórico fica em memória por padrão —
passe `A2AHandler(agent, store=meu_dict)` para plugar persistência.

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
