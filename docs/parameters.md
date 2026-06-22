# Parâmetros de geração e perfis por modelo

A jangada aceita **nomes canônicos** de parâmetros e cada adapter os traduz para
o nome nativo do SDK, descartando os não suportados.

## Parâmetros canônicos

| Canônico      | OpenAI/Groq            | Anthropic        | Gemini                |
|---------------|------------------------|------------------|-----------------------|
| `temperature` | `temperature`          | `temperature`    | `temperature`         |
| `max_tokens`  | `max_tokens`           | `max_tokens`     | `max_output_tokens`   |
| `top_p`       | `top_p`                | `top_p`          | `top_p`               |
| `top_k`       | *(descartado)*         | `top_k`          | `top_k`               |
| `stop`        | `stop`                 | `stop_sequences` | `stop_sequences`      |
| `seed`        | `seed`                 | *(descartado)*   | `seed`                |

```python
llm = LLM("anthropic", "claude-opus-4-8", temperature=0.2, max_tokens=512)

# override por chamada
llm.complete("...", params={"temperature": 0.9})

# clone com novos defaults
criativo = llm.with_params(temperature=1.0)
```

Parâmetros específicos de um SDK que não têm nome canônico vão via `extra=`.

## Perfis automáticos (quirks por modelo)

Modelos do mesmo provider às vezes têm contratos diferentes. A jangada normaliza
isso em `profiles.py`, **por modelo**, sem você precisar saber:

- `gpt-5` rejeita `temperature` (HTTP 400) e exige `max_completion_tokens`.
- `gemini-3.x` descarta `temperature`/`top_p`/`top_k` e troca `thinking_budget`
  por `thinking_level`.

Ordem aplicada no adapter: `_translate()` (canônico → nativo) →
`apply_profile()` (quirks de modelo). Ao suportar um modelo novo com contrato
diferente, adicione uma regra em `profiles.py` em vez de espalhar `if`s.

Veja [Providers](providers.md) e [Estendendo](extending.md).
