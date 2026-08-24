# DeepSeek

Provider `deepseek`. Adapter sobre o SDK `openai` apontando para o `base_url`
próprio do [DeepSeek](https://api-docs.deepseek.com) — mesma receita do
[OpenRouter](providers.md#openrouter-gateway-para-centenas-de-modelos): fala o
dialeto `chat.completions`, só troca a URL e a chave.

```bash
pip install "jangada-ai[openai]"
```

- **`provider=`**: `"deepseek"`
- **Variável de ambiente**: `DEEPSEEK_API_KEY`
- **Base do adapter**: `_OpenAICompatible` (mesma da OpenAI/Groq/OpenRouter)

```python
from jangada_ai import LLM

llm = LLM("deepseek", "deepseek-v4-flash")   # rápido/barato
print(llm.complete("Olá!").text)
```

## Modelos

- **`deepseek-v4-flash`** — rápido e barato, uso geral.
- **`deepseek-v4-pro`** — modelo de raciocínio (thinking mode), mais caro.
- **`deepseek-v4-flash-vision-exp`** — vision, experimental.

## O que faz

- **Texto** (`complete`/`acomplete`) e **streaming** (`stream`/`astream`).
- **Vision** (`images=`, só `deepseek-v4-flash-vision-exp`): imagens viram
  `image_url` com data URI, mesmo caminho dos outros providers OpenAI-compatíveis.
- **Tools / function calling**: suportado, formato OpenAI padrão.
- **Documentos** (`files=`): extração de texto local (comum a todos).
- **Structured output** (`parse`/`aparse`): **sem** JSON Schema estrito — a doc
  do DeepSeek é explícita ("does not offer a schema-based mode"). O adapter vai
  direto para **JSON Object mode** (schema injetado como instrução de sistema +
  `response_format={"type":"json_object"}`), sem tentar `json_schema` antes
  (diferente do fallback do Groq/OpenRouter, que tentam json_schema primeiro).

## Modo `thinking` (raciocínio)

`deepseek-v4-pro` e `deepseek-v4-flash` suportam um modo de raciocínio
explícito. É um campo **fora do schema típado do SDK oficial da OpenAI** — sem
tratamento especial, `client.chat.completions.create(thinking=...)` levantaria
`TypeError`. O adapter da jangada resolve isso: passe `thinking` normalmente
via `extra=` e ele empacota em `extra_body` por baixo dos panos.

```python
llm = LLM("deepseek", "deepseek-v4-pro")
comp = llm.complete(
    "Resolva: se 3 maçãs custam R$ 6, quanto custam 7?",
    extra={"thinking": {"type": "enabled", "reasoning_effort": "high"}},  # low/high/max
)
```

⚠️ Nesse modo a API **rejeita** `temperature`/`top_p`/`presence_penalty`/
`frequency_penalty` — não passe esses params junto com `thinking` habilitado.

A resposta crua (`comp.raw`) traz o campo não-padrão `reasoning_content` (o
"pensamento" do modelo, separado do `content` final) quando o modo está ativo —
a jangada não expõe isso como campo de primeira classe em `Completion`; acesse
via `comp.raw.choices[0].message.reasoning_content` se precisar.

## O que NÃO suporta (levanta erro claro)

- **MCP server-side** (`mcp_servers=`): a Responses API do DeepSeek só tem
  `function`/`web_search` — `mcp` está explicitamente na lista de tipos
  ignorados. Levanta `UnsupportedError`.
- **Transcrição de áudio** (`transcribe`/`atranscribe`): sem endpoint
  documentado. Levanta `UnsupportedError`.
- **Embeddings** (`embed`): sem endpoint documentado (não implementado).

## Preço e cache

O DeepSeek tem preço diferenciado por **horário** (pico/fora de pico, UTC) e
por **cache hit/miss** no prompt (prefixos repetidos custam menos). A tabela de
preços da jangada (`pricing.py`) usa um valor **aproximado único** por modelo —
não modela essas variações. Para custo exato, confira `comp.raw.usage`
(`prompt_cache_hit_tokens`/`prompt_cache_miss_tokens`) e a
[página de preços oficial](https://api-docs.deepseek.com/quick_start/pricing).

Relacionado: [OpenRouter](providers.md#openrouter-gateway-para-centenas-de-modelos),
[Groq](llm-groq.md), [Matriz de capacidades](capabilities.md),
[Providers e chaves](providers.md).
