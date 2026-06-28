# Casos de uso (do problema ao código)

Três cenários reais resolvidos com a jangada — do problema ao código rodável.
Cada um troca de provider/model sem mudar a lógica.

## 1. Extração estruturada de nota fiscal (visão + Pydantic)

**Problema:** você recebe fotos/PDFs de notas fiscais e precisa dos campos
(emitente, valor, itens) como dados, não como texto solto. OCR + regex quebra
fácil; você quer um objeto validado.

**Solução:** `parse()` com um modelo Pydantic e a imagem em `images=`. Funciona
em qualquer provider com visão — a estratégia de structured output (OpenAI
`.parse`, Gemini `response_schema`, Anthropic tool-forcing) é escolhida por baixo.

```python
from pydantic import BaseModel, Field
from jangada_ai import LLM, Image

class Item(BaseModel):
    descricao: str
    valor: float

class NotaFiscal(BaseModel):
    emitente: str
    cnpj: str | None = None
    total: float = Field(description="Valor total em reais")
    itens: list[Item]

llm = LLM("openai", "gpt-4o-mini")   # ou gemini/anthropic — mesma chamada
nota = llm.parse(
    "Extraia os dados desta nota fiscal.",
    NotaFiscal,
    images=[Image.from_path("nota.jpg")],
).parsed

print(nota.emitente, nota.total, len(nota.itens), "itens")
```

> PDF com camada de texto? Use `files=["nota.pdf"]` — a jangada extrai o texto
> localmente (mais barato, sem precisar de vision). Veja [Documentos](documents.md).

## 2. Fallback por erro entre providers (resiliência)

**Problema:** um provider cai (rate limit, 5xx, timeout) e sua aplicação para. Você
quer que a chamada caia automaticamente para outro modelo/provider só quando faz
sentido — sem mascarar erro de credencial ou de payload.

**Solução:** `fallbacks=` (ou `with_fallback`). A jangada tenta com retry+backoff
no primeiro candidato e só faz failover nos erros que valem (rate limit, timeout,
5xx, 404) — `DEFAULT_FAILOVER`. Custo e usage agregam normalmente.

```python
from jangada_ai import LLM

primario = LLM("anthropic", "claude-opus-4-8", max_retries=2)
llm = primario.with_fallback(
    LLM("openai", "gpt-4o-mini"),
    LLM("groq", "llama-3.3-70b-versatile"),
)

comp = llm.complete("Resuma em 1 frase: {{texto}}", texto="...")
print(comp.text, "via", comp.provider)   # mostra qual provider respondeu
```

> Auth e bad_request **não** entram no failover por padrão (trocar de provider não
> conserta chave errada nem payload inválido). Veja [Retry e fallback](retry-fallback.md).

## 3. RAG: responder com base nos seus documentos

**Problema:** o modelo não conhece seus dados internos (manuais, políticas, base
de conhecimento) e inventa respostas. Você quer respostas ancoradas nos seus
textos, com citação implícita do trecho usado.

**Solução:** o módulo `jangada_ai.rag` (extra `[rag]`): indexa (chunk → embed →
store) e responde buscando o contexto relevante. Em memória para começar; troque a
string de conexão para pgvector/Mongo em produção, sem mudar o código.

```python
from jangada_ai import LLM
from jangada_ai.rag import RAG, vector_store

emb = LLM("openai", "text-embedding-3-small")
chat = LLM("openai", "gpt-4o-mini")
store = vector_store("memory")          # troque por "postgresql://..." em produção

rag = RAG(emb, store, chat=chat, k=5)
rag.add_document("politica.md", metadata={"fonte": "rh"})   # extrai -> chunk -> embed -> grava
resp = rag.ask("Qual o prazo de reembolso?", mode="hybrid")
print(resp.text)
```

> Para qualidade em produção: reranking, semantic chunking e estratégias
> (`multi_query`/`parent_document`/`compress`). Veja [RAG](rag.md).
