# AWS Bedrock

Provider `bedrock`. Adapter sobre o `boto3` (`bedrock-runtime`) usando a
**Converse API** — a interface unificada do Bedrock para chat: mensagens
multi-turno, vision e *tool use* funcionam com Claude, Llama, Mistral, Nova etc.
sem mudar o shape do payload.

```bash
pip install "jangada-ai[bedrock]"
```

- **`provider=`**: `"bedrock"`
- **Credenciais**: a cadeia padrão do boto3 (`AWS_ACCESS_KEY_ID`/
  `AWS_SECRET_ACCESS_KEY`, perfil `~/.aws/credentials`, role da instância...).
  **Não** há `env_key` de API key.
- **Região**: `AWS_REGION`/`AWS_DEFAULT_REGION` ou `region_name=` no construtor.

```python
from jangada_ai import LLM

llm = LLM("bedrock", "us.anthropic.claude-3-5-sonnet-20241022-v2:0", region_name="us-east-1")
print(llm.complete("Olá!").text)
```

O `model` é o **id do modelo** ou de um **inference profile** do Bedrock (ex.:
`anthropic.claude-3-haiku-20240307-v1:0`, `us.anthropic.claude-3-5-sonnet-...`).

## O que faz

- **Texto** (`complete`/`acomplete`) via `converse`.
- **Streaming** (`stream`/`astream`) via `converse_stream`.
- **Structured output** (`parse`): *tool-forcing* (uma tool `extract` com o JSON
  Schema do modelo Pydantic + `toolChoice` fixo) — mesma estratégia do Anthropic.
  Funciona nos modelos que aceitam tool use (Claude, Nova, Mistral Large...).
- **Tools** (`tools=`/`tool_choice=`): `toolConfig` da Converse API.
- **Vision** (`images=`): blocos `image` com `source.bytes`.

## Sync e async

O `boto3` é **síncrono**. A paridade async (`acomplete`/`aparse`/`astream`) sai
de `asyncio.to_thread` — não há cliente async oficial do Bedrock. A interface da
jangada é a mesma dos outros providers.

## Quirks

- **`top_k`/`seed`** não entram no `inferenceConfig` padrão da Converse
  (`maxTokens`/`temperature`/`topP`/`stopSequences`). Params específicos de
  modelo vão via `extra=` → `additionalModelRequestFields` quando o modelo aceita.
- **MCP server-side não é suportado** pela jangada no Bedrock — use `MCPClient`/
  `run_agent` (client-side) ou os providers Anthropic/OpenAI/Groq.
- **Erros do botocore** são normalizados por `errors.classify()` (status HTTP em
  `response['ResponseMetadata']`) para a hierarquia única — retry e fallback
  funcionam igual.
- **`stopReason: "max_tokens"`** é normalizado para `finish_reason="length"`.

Relacionado: [Anthropic](llm-anthropic.md) (mesma estratégia de structured),
[Matriz de capacidades](capabilities.md), [Providers e chaves](providers.md).
