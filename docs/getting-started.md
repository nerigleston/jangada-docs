# Começando com jangada

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/nerigleston/jangada-docs/blob/main/examples/notebooks/jangada_quickstart.ipynb)

`jangada` é uma camada fina sobre os SDKs oficiais de LLM (Anthropic, OpenAI,
Groq, Gemini). O objetivo é trocar **provider / model / api_key** sem mudar o
resto do código.

> Quer só testar? Abra o **[quickstart no Colab](https://colab.research.google.com/github/nerigleston/jangada-docs/blob/main/examples/notebooks/jangada_quickstart.ipynb)** (1 clique, cole sua chave e rode).

## Instalação

```bash
pip install jangada-ai                 # nome no PyPI; importa-se como jangada_ai
pip install "jangada-ai[anthropic]"    # só Claude
pip install "jangada-ai[openai,groq]"  # OpenAI + Groq
pip install "jangada-ai[all]"          # todos os SDKs
pip install "jangada-ai[files]"        # leitura de docx/pdf/csv/xlsx
```

> O nome de distribuição é `jangada-ai` (o nome `jangada` estava ocupado no
> PyPI). O pacote é importado como `import jangada_ai` (hífen vira underscore).

Imports são preguiçosos: `import jangada_ai` funciona sem nenhum SDK instalado.

## Primeira chamada

```python
from jangada_ai import LLM

llm = LLM("anthropic", "claude-opus-4-8")
print(llm.complete("Explique {{tema}} em 2 frases.", tema="MCP").text)
```

`complete()` aceita templates `{{ }}` direto no prompt — as variáveis vêm como
keyword args. Veja [Parâmetros de geração](parameters.md) para controlar
`temperature`, `max_tokens`, etc.

## Trocar de provider

Só muda os dois primeiros argumentos; o resto do código permanece:

```python
LLM("openai", "gpt-4o-mini")
LLM("groq", "llama-3.3-70b-versatile")
LLM("gemini", "gemini-2.5-flash")
```

Chaves de API vêm de `api_key=`, da variável de ambiente do provider, ou de um
arquivo `.env` detectado na importação. Precedência:
`api_key=` explícito > variável de ambiente > `.env`.

## Próximos passos

- [Providers e chaves](providers.md)
- [Structured output](structured-output.md)
- [Documentos (docx/pdf/csv/xlsx)](documents.md)
- [Retry e fallback](retry-fallback.md)
