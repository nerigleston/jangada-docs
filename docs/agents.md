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
  `mcp_allowed_tools=[...]` restringe quais tools do MCP ficam visíveis.
  `mcp_tools_cache=[...]` pula o `list_tools()` (e o round-trip) toda vez que
  `arun`/`astream` roda — liste uma vez com `await mcp_tools(mcp_client)` e
  passe aqui; sem isso, cada chamada relista as tools do zero.
  `mcp_allowed_tools` continua sendo aplicado por cima de `mcp_tools_cache`
  (filtra a lista já pronta), então dá pra listar sem filtro e restringir
  por instância de `Agent`.
- **`AgentResult.stopped_by_limit`**: `True` quando o loop parou por bater em
  `max_iterations` com `tool_calls` ainda pendentes — nesse caso `text`/
  `messages` NÃO são a resposta final do modelo, são o último passo do loop
  (um `UserWarning` também é emitido). `False` quando o modelo parou de pedir
  tool por conta própria.
- **`on_tool_call`/`on_tool_result`**: callbacks (sync no `run`; sync ou async
  no `arun`) que correm a cada tool call (function ou MCP). `on_tool_call`
  devolvendo `False` **veta** a chamada (o modelo recebe um `tool_result` de
  erro, sem a tool executar). `AgentResult.tool_trace` traz `{"call",
  "result", "is_error"}` de todas as chamadas do turno.

```python
def confirma(call):
    return call.name != "apagar_tudo"   # veta essa tool específica

agente = Agent(llm, role="Operador", tools=[apagar_tudo, listar],
               on_tool_call=confirma, on_tool_result=lambda c, r: print(c.name, r.is_error))
res = agente.run("Liste e apague tudo")
print(res.tool_trace)   # [{"call": ToolCall(...), "result": "...", "is_error": True/False}, ...]
```

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
| `GET /.well-known/agent-card.json` (e o legado `/.well-known/agent.json`) | Agent Card do agente principal |
| `GET /agents` | catálogo (lista de Agent Cards) |
| `POST /` | JSON-RPC `message/send` (JSON), `message/stream` (SSE), `tasks/get`, `tasks/cancel` |
| `POST /agents/{name}` | idem, para um agente específico do catálogo |

Para um time descobrível, passe uma lista: `build_a2a_app([sofia_h, orcamento_h])`.
A **lógica do protocolo** vive em `A2AHandler` (Python puro, testável sem rede); o
servidor ASGI importa Starlette só aqui. O histórico fica em memória por padrão —
passe `A2AHandler(agent, store=meu_dict)` para plugar persistência.

### Multi-tenant: agente resolvido por request

Em vez de um agente fixo, passe um **`resolver`** que recebe o **contexto da
requisição** (headers/auth) e devolve o `Agent` certo para aquele request — útil
quando o agente é montado por tenant (ex.: tools com closure no `tenant_id` do
JWT). Com `tenant_key`, o histórico fica **isolado por tenant**.

```python
def resolver(ctx):                       # ctx = {"headers": {...}, "auth": "Bearer ..."}
    tenant = (ctx.get("auth") or "").removeprefix("Bearer ")
    return build_sofia(tenant_id=tenant)

handler = A2AHandler(resolver=resolver, name="Sofia",
                     tenant_key=lambda c: c.get("auth", ""))
app = build_a2a_app(handler)             # extrai o contexto do request por padrão
```

Tudo é opcional (o modo fixo `A2AHandler(agent)` segue igual). Os parâmetros:
`resolver` (exclui `agent`), `name` (obrigatório com `resolver`), `description`,
`tenant_key` (isola histórico), e `context_factory=` no `build_a2a_app` (como
montar o contexto a partir do `Request` — troque para validar/decodificar o JWT).
A lib **não** decodifica JWT: o contexto traz os headers crus e o `Authorization`.

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

Cada agente roda em ordem e recebe, por padrão, **apenas a saída do agente
anterior** como contexto (não o transcript acumulado):

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

**Semântica do contexto** (`context=`):

- **`"last"`** (padrão): cada agente recebe só a saída imediatamente anterior. O
  input por salto é ~constante — o custo da cadeia cresce **O(N)**, não O(N²).
- **`"full"`**: cada agente recebe o **transcript acumulado** (todas as saídas
  anteriores, rotuladas por papel). Mais contexto, custo **O(N²)** em cadeias longas.

```python
Squad([pesquisador, escritor], context="full")   # transcript inteiro a cada salto
```

**Observabilidade por agente**: `res.steps` traz uma entrada por agente com
`(role, usage, cost, cost_complete, dt)` — dá para ver o input/custo/latência
crescer (ou não) a cada salto sem desmontar o `Squad` na mão.

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

## O que mudou na 1.9.0

- **Squad hierárquico de verdade assíncrono.** No `Squad.arun`, a tool de
  delegação é `async` e chama `await membro.arun()` — o event loop não trava e o
  membro mantém `mcp_client` e tools async. O gerente é uma **cópia** do agente
  original, então `on_tool_call` (veto), `on_tool_result`, MCP e memória valem
  também no modo hierárquico.
- **Custo e rastro dos membros.** `SquadResult.usage`/`cost` somam o gerente **e**
  os membros delegados (`cost_complete` só é `True` se todos tiverem preço);
  `outputs` traz a saída de cada membro e `steps` uma entrada por delegação.
  Papéis repetidos viram chaves únicas (`Revisor`, `Revisor#2`).
- **Nomes das tools de delegação** são transliterados (acentos saem), deduplicados
  com sufixo (`_2`, `_3`) e truncados em 64 caracteres.
- **`Agent.astream(prompt, chunk_size=24)`**: sem tools faz streaming real do
  provider; com tools resolve o loop com `acomplete` e emite o texto final em
  pedaços (sem gerar a resposta duas vezes). Ao terminar, `agent.last_stream_result`
  traz o `AgentResult` (usage, cost, `tool_trace`, `stopped_by_limit`).
- **Tools nativas misturadas.** `Agent(llm, tools=[web_search(), minha_funcao])`
  funciona: a tool nativa roda no provider e aparece no `tool_trace` com
  `"server": True` (veja [Tools nativas](native-tools.md)).
- **MCP: allowlist aplicada na execução.** Uma tool MCP que não foi oferecida ao
  modelo (fora de `mcp_allowed_tools`) **não é executada** — volta como
  `tool_result` de erro, mesmo que o modelo invente o nome.
- **Parâmetro `BaseModel` em tools** recebe a instância validada do modelo
  (`jangada_ai.coerce_args`).
- **`plan()`** levanta `ValueError` claro se a resposta vier sem `parsed`;
  `RAGMemory` loga falhas (logger `jangada_ai`) em vez de engoli-las e não grava
  turnos que pararam por limite.

### A2A (card e servidor)

`Agent.card()` segue a spec A2A ≥ 0.3: traz `protocolVersion` (padrão `"0.3.0"`) e
`preferredTransport="JSONRPC"`, aceita `security_schemes=`/`security=`, e os
parâmetros das tools viram `tags` (o campo `skills[].parameters`, fora da spec,
saiu). O `A2AHandler` serve o card em **`/.well-known/agent-card.json`** (e mantém
`/.well-known/agent.json`), limita memória com `max_tasks`/`task_ttl` e
`max_contexts`/`context_ttl` (padrão 1000 itens / 1 h), isola `tasks/get|cancel`
por tenant, devolve `-32002` ao cancelar task já terminada, `-32700`/`-32600`/
`-32602` para JSON inválido/corpo inválido/pergunta vazia, e não expõe a mensagem
da exceção no `-32603` (o detalhe vai para o log).

```python
from jangada_ai import Agent, LLM, Squad, web_search

pesquisador = Agent(LLM("anthropic", "claude-sonnet-5"), role="Pesquisador",
                    tools=[web_search(max_uses=3)])
redator = Agent(LLM("openai", "gpt-5-mini"), role="Redator")
gerente = Agent(LLM("openai", "gpt-5"), role="Gerente")

res = await Squad([pesquisador, redator], manager=gerente).arun("Resuma as novidades do Python 3.14")
print(res.text, res.cost, res.outputs.keys(), len(res.steps))
```

## Como se relaciona com o resto

Não há mágica nem infra nova: `Agent` é o loop de tool calling (como o
[`run_agent`](mcp.md)); a memória é o [RAG](rag.md); o `Squad` hierárquico usa
delegação por tools ([Tools](tools.md)). Você pode trocar o provider de qualquer
agente sem mudar mais nada — a tese da jangada vale também aqui.
