# Providers e chaves de API

A jangada suporta quatro providers, cada um isolado em um *adapter* que traduz
os tipos normalizados (`Message`/`Completion`) para o SDK nativo.

| Provider    | `provider=` | Variável de ambiente | Extra para instalar         |
|-------------|-------------|----------------------|-----------------------------|
| Anthropic   | `anthropic` | `ANTHROPIC_API_KEY`  | `jangada-ai[anthropic]`     |
| OpenAI      | `openai`    | `OPENAI_API_KEY`     | `jangada-ai[openai]`        |
| Groq        | `groq`      | `GROQ_API_KEY`       | `jangada-ai[groq]`          |
| Gemini      | `gemini`    | `GEMINI_API_KEY`     | `jangada-ai[gemini]`        |

## Resolução da chave

```python
LLM("openai", "gpt-4o-mini", api_key="sk-...")   # explícito
LLM("openai", "gpt-4o-mini")                       # usa OPENAI_API_KEY ou .env
```

Precedência: **`api_key=` explícito > variável de ambiente > arquivo `.env`**.
O `.env` é detectado de forma não-destrutiva na importação (desative com
`JANGADA_NO_DOTENV=1`).

## Como cada adapter trata structured output

- **OpenAI**: `chat.completions.parse(response_format=Modelo)` → `.message.parsed`
- **Groq**: `response_format={"type":"json_schema",...}` + `model_validate_json`
- **Gemini**: `config.response_schema=Modelo` → `resp.parsed`
- **Anthropic**: tool-forcing (`tool_choice` fixo) → valida `tool_use.input`

Veja [Structured output](structured-output.md) para o uso uniforme.

## Adicionando um provider novo

Se ele falar o dialeto `chat.completions` da OpenAI, herde de
`_OpenAICompatible` e ajuste `sdk_module`/`sync_class`/`async_class`. Caso
contrário, implemente os 6 métodos do contrato `Provider`. Detalhes em
[Estendendo](extending.md).
