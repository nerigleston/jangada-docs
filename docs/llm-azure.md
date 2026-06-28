# Azure OpenAI

Provider `azure`. Adapter sobre o SDK `openai` usando o cliente `AzureOpenAI` —
a **mesma API** (`chat.completions`/`responses`) da OpenAI, servida pela Azure.
Reusa todo o adapter `_OpenAICompatible`.

```bash
pip install "jangada-ai[openai]"
```

- **`provider=`**: `"azure"`
- **Variável de ambiente**: `AZURE_OPENAI_API_KEY`
- **Endpoint**: `AZURE_OPENAI_ENDPOINT` (ou `azure_endpoint=` no construtor)
- **Versão da API**: `OPENAI_API_VERSION` (ou `api_version=`; default estável recente)
- **Base do adapter**: `_OpenAICompatible` (mesmo da OpenAI/Groq)

```python
from jangada_ai import LLM

# O "model" é o NOME DO DEPLOYMENT na Azure (não o nome do modelo base).
llm = LLM("azure", "meu-deploy-gpt4o")
print(llm.complete("Olá!").text)
```

## Detalhe importante: `model` = deployment

Na Azure você cria *deployments* de um modelo base e dá um nome a cada um. A
jangada usa esse **nome do deployment** como `model`. Ex.: se você criou um
deployment chamado `gpt4o-prod` do `gpt-4o`, use `LLM("azure", "gpt4o-prod")`.

## O que faz

- **Texto** (`complete`/`acomplete`) e **streaming** (`stream`/`astream`).
- **Structured output** (`parse`): helper nativo `chat.completions.parse`
  (`.message.parsed`) — igual à OpenAI.
- **Vision** (`images=`): imagens viram `image_url` com data URI.
- **Documentos** (`files=`): extração de texto local (comum a todos).
- **Embeddings** (`embed`): deployment de `text-embedding-*`.
- **Transcrição** (`transcribe`): deployment de modelo de áudio (`whisper`/`gpt-4o-transcribe`).

## Config por ambiente

```bash
export AZURE_OPENAI_ENDPOINT="https://seu-recurso.openai.azure.com"
export AZURE_OPENAI_API_KEY="..."
export OPENAI_API_VERSION="2024-10-21"   # opcional
```

Ou direto no construtor:

```python
llm = LLM("azure", "meu-deploy", azure_endpoint="https://...", api_version="2024-10-21")
```

## Quirks

- **Perfis de modelo** (`profiles.py`) valem pelo nome do modelo base — como o
  `model` é o nome do deployment, perfis como o do `gpt-5` só pegam se o
  deployment tiver esse nome. Passe params específicos via `extra=`/`params=`
  quando precisar.
- O restante (erros normalizados, retry, fallback, custo) é idêntico à OpenAI.

Relacionado: [OpenAI](llm-openai.md), [Matriz de capacidades](capabilities.md),
[Providers e chaves](providers.md).
