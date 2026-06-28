# Vertex AI

Provider `vertex`. Os modelos **Gemini** servidos pelo **Google Cloud / Vertex
AI**, via `google-genai` em modo Vertex (`vertexai=True`). Herda todo o adapter
do [Gemini](llm-gemini.md) — mesma tradução, vision, thinking, structured e
streaming. Só muda a **autenticação**.

```bash
pip install "jangada-ai[gemini]"
```

- **`provider=`**: `"vertex"`
- **Autenticação**: **ADC** (Application Default Credentials) — não usa API key.
  `gcloud auth application-default login` ou uma service account
  (`GOOGLE_APPLICATION_CREDENTIALS`).
- **Projeto/região**: `GOOGLE_CLOUD_PROJECT` e `GOOGLE_CLOUD_LOCATION` (ou
  `project=`/`location=` no construtor; `location` default `us-central1`).

```python
from jangada_ai import LLM

llm = LLM("vertex", "gemini-2.5-flash")  # project/location vêm do ambiente
print(llm.complete("Olá!").text)
```

## Vertex × Gemini (API key)

| | `gemini` | `vertex` |
|---|---|---|
| Autenticação | `GEMINI_API_KEY`/`GOOGLE_API_KEY` | ADC + projeto GCP |
| Cliente | `genai.Client(api_key=...)` | `genai.Client(vertexai=True, project=, location=)` |
| Recursos | iguais (texto, vision, thinking, structured, streaming, embeddings) | iguais |

Use `vertex` quando seu time já está no Google Cloud (billing, IAM, VPC,
data residency por região). Para um começo rápido com API key, use `gemini`.

## O que faz

Tudo que o provider `gemini` faz (é a mesma classe por baixo):

- **Texto**, **streaming**, **structured output** (`response_schema`), **vision**,
  **tools/function calling**, **thinking** (`thinking_budget`/`thinking_level`),
  **embeddings** e **transcrição** (multimodal).

## Quirks

- Os mesmos do [Gemini](llm-gemini.md): perfis por modelo (`gemini-3.x` troca
  `thinking_budget` por `thinking_level`), `max_tokens`→`max_output_tokens`,
  `stop`→`stop_sequences`.
- **MCP client-side** (sessão) só no async, como no Gemini; MCP remoto por URL
  não é suportado.

Relacionado: [Gemini](llm-gemini.md), [Matriz de capacidades](capabilities.md),
[Providers e chaves](providers.md).
