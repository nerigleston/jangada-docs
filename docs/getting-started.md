# Começando com jangada

`jangada` é uma camada fina sobre os SDKs oficiais de LLM (Anthropic, OpenAI,
Groq, Gemini). O objetivo é trocar **provider / model / api_key** sem mudar o
resto do código.

## Instalação

```bash
pip install jangada-ai                 # nome no PyPI (import segue "jangada")
pip install "jangada-ai[anthropic]"    # só Claude
pip install "jangada-ai[openai,groq]"  # OpenAI + Groq
pip install "jangada-ai[all]"          # todos os SDKs
pip install "jangada-ai[files]"        # leitura de docx/pdf/csv/xlsx
```

> O nome de distribuição é `jangada-ai` (o nome `jangada` estava ocupado no
> PyPI), mas o pacote importado continua `import jangada`.

Imports são preguiçosos: `import jangada` funciona sem nenhum SDK instalado.

## Primeira chamada

```python
from jangada import LLM

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
