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

> ⚠️ `max_tokens` tem default de **1024**. Em listas grandes a resposta pode ser
> cortada; nesse caso a jangada levanta `errors.TruncatedError` ("aumente
> max_tokens") **antes** de validar — em vez de um erro confuso de JSON cortado do
> Pydantic. A correção é subir `max_tokens` (ver [Parâmetros](parameters.md)).

## Async

```python
comp = await llm.aparse("Extraia: ...", Pessoa)
```

## Como cada provider resolve

| Provider  | Mecanismo                                                |
|-----------|----------------------------------------------------------|
| OpenAI    | `chat.completions.parse(response_format=Modelo)`         |
| Groq      | `json_schema` quando o modelo suporta; senão **JSON Object mode** |
| Gemini    | `config.response_schema=Modelo` → `resp.parsed`          |
| Anthropic | tool-forcing (`tool_choice` fixo) → valida `tool_use`    |

Você não precisa saber qual é qual — `parse()`/`aparse()` cuidam disso. Use
Pydantic v2 (`model_json_schema()`, `model_validate`).

> **Groq — funciona em qualquer modelo.** Só alguns modelos do Groq aceitam
> `json_schema` (ex.: `openai/gpt-oss-*`, `llama-4-scout`). Para os demais (ex.:
> `llama-3.3-70b-versatile`), a jangada **cai automaticamente para JSON Object
> mode**: injeta o schema na instrução, pede um objeto JSON e valida com Pydantic.
> Você chama `parse()` igual — sem saber o que o modelo suporta.

Funciona junto com [Vision](vision.md) e [Documentos](documents.md): passe
`images=` ou `files=` na mesma chamada `parse()`.

## Exemplo

[`examples/structured_example.py`](https://raw.githubusercontent.com/nerigleston/jangada-docs/main/examples/structured_example.py) — script executável.
