# Por que jangada (comparativo honesto)

Existem ótimas ferramentas no ecossistema. Esta página é um comparativo direto e
honesto com LiteLLM, LangChain e instructor — **quando usar cada uma** e onde a
jangada brilha. Nenhuma "ganha" sempre; depende do que você está construindo.

## Resumo

| | Foco | Quando escolher |
|---|---|---|
| **jangada** | Camada fina PT-BR sobre os SDKs oficiais, troca de provider sem mudar o código, com structured/vision/áudio/RAG/agentes compostos e observability em 1 linha no `.env` | Você quer trocar provider/model facilmente, tipos normalizados, retry+fallback por erro e docs/erros em PT-BR — sem framework pesado |
| **LiteLLM** | Proxy/gateway unificado para 100+ providers, com billing/keys/roteamento | Você precisa de um **gateway** central (muitos providers, controle de custo/cota por time, balanceamento) |
| **LangChain** | Framework amplo de orquestração (chains, agents, integrações) | Você quer um ecossistema grande de integrações prontas e não se importa com a superfície/abstrações |
| **instructor** | Structured output (Pydantic) sobre os SDKs | Seu único problema é "quero a resposta como objeto Pydantic confiável" |

## jangada × LiteLLM

- **LiteLLM** cobre muitíssimos providers e é forte como **proxy** (servidor com
  chaves, orçamento, roteamento, logging centralizado). Se você quer um ponto
  único de billing/cota para vários times, é a escolha natural.
- **jangada** é uma **biblioteca**, não um gateway: a complexidade de cada SDK
  fica num adapter, e você programa contra `Message`/`Completion`. O foco é a
  ergonomia de quem escreve a aplicação (retry+fallback por *tipo de erro*,
  normalização de params **por modelo** — `gpt-5`, `gemini-3.x` —, custo na
  resposta, structured uniforme), com docs e mensagens de erro em **PT-BR**.
- **Use os dois juntos:** aponte um provider OpenAI-compat da jangada para o proxy
  do LiteLLM (`base_url=`) e tenha o melhor dos dois.

## jangada × LangChain

- **LangChain** é um framework grande, com um ecossistema enorme de integrações
  (vector stores, loaders, tools). Se você quer "tudo já existe" e aceita a curva
  de abstrações (LCEL, runnables), ele entrega.
- **jangada** é deliberadamente **fina**: sem dependências pesadas no core (só
  `pydantic`), imports preguiçosos (`import jangada_ai` funciona sem SDK), e uma
  API pequena. Agentes/`Squad`/RAG são **composição** sobre o núcleo, não uma
  infra paralela. Você lê o código todo numa tarde.
- **Quando a jangada brilha:** apps que precisam de portabilidade entre providers,
  observability sem boilerplate e um código que você consegue auditar inteiro.
- **Quando LangChain brilha:** quando você depende de muitas integrações de
  terceiros que ele já tem e não quer escrevê-las.

## jangada × instructor

- **instructor** resolve muito bem **um** problema: structured output Pydantic
  confiável sobre os SDKs. Se é só isso que você precisa, é leve e excelente.
- **jangada** faz structured output uniforme (`parse()` — OpenAI `.parse`, Groq
  `json_schema` com fallback p/ JSON Object mode, Gemini `response_schema`,
  Anthropic/Bedrock tool-forcing) **e** o resto: troca de provider, vision, áudio,
  tools/MCP, retry+fallback, custo, cache, RAG, agentes e observability.
- **Regra prática:** só precisa de "texto → Pydantic"? instructor serve. Precisa
  disso **dentro** de uma app multi-provider com resiliência e observability? jangada.

## Onde a jangada claramente brilha

- **Trocar provider/model/api_key sem tocar no resto do código** — incluindo
  Azure OpenAI, AWS Bedrock e Vertex AI, além de Anthropic/OpenAI/Groq/Gemini/OpenRouter.
- **Retry + fallback por tipo de erro** (rate limit/5xx/timeout/404 → failover;
  auth/bad_request não), com backoff — não um try/except genérico.
- **Normalização por modelo** (`profiles.py`): quirks de `gpt-5`/`gemini-3.x`
  resolvidos por você.
- **Observability em 1 linha no `.env`** — cada chamada vira um trace, zero
  boilerplate.
- **PT-BR de ponta a ponta:** docs, exemplos e mensagens de erro.

## Onde ela não é a melhor escolha

- Você precisa de um **gateway/proxy central** com billing por time → LiteLLM.
- Você quer um **catálogo gigante de integrações** prontas → LangChain.
- Seu escopo é **só** structured output e nada mais → instructor.
