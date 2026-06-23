# Structured output (Pydantic)

Uma só chamada `parse()` devolve uma instância Pydantic validada, independente
de como cada provider implementa isso por baixo.

```python
from pydantic import BaseModel
from jangada_ai import LLM

class Pessoa(BaseModel):
    nome: str
    idade: int

llm = LLM("openai", "gpt-4o-mini")
comp = llm.parse("Extraia: João tem 30 anos.", Pessoa)
print(comp.parsed.nome, comp.parsed.idade)   # João 30
```

- `comp.parsed` → a instância Pydantic.
- `comp.text` → o JSON bruto retornado.
- `comp.usage` / `comp.cost` → tokens e custo estimado.

## Async

```python
comp = await llm.aparse("Extraia: ...", Pessoa)
```

## Como cada provider resolve

| Provider  | Mecanismo                                                |
|-----------|----------------------------------------------------------|
| OpenAI    | `chat.completions.parse(response_format=Modelo)`         |
| Groq      | `response_format={"type":"json_schema",...}` + validação |
| Gemini    | `config.response_schema=Modelo` → `resp.parsed`          |
| Anthropic | tool-forcing (`tool_choice` fixo) → valida `tool_use`    |

Você não precisa saber qual é qual — `parse()`/`aparse()` cuidam disso. Use
Pydantic v2 (`model_json_schema()`, `model_validate`).

Funciona junto com [Vision](vision.md) e [Documentos](documents.md): passe
`images=` ou `files=` na mesma chamada `parse()`.

## Exemplo

[`examples/structured_example.py`](https://raw.githubusercontent.com/nerigleston/jangada-docs/main/examples/structured_example.py) — script executável.
