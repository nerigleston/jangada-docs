# RAG (embeddings + busca vetorial/híbrida)

A jangada cobre as partes "de LLM" do RAG (embeddings + montar o contexto) e traz
um módulo `jangada_ai.rag` opcional com chunking, vector store (pgvector/Mongo)
e busca híbrida.

```bash
pip install "jangada-ai[rag]"   # psycopg (pgvector) + pymongo (Mongo)
```

## Embeddings (`embed`)

Capacidade opcional, igual ao áudio: **OpenAI e Gemini** suportam; **Anthropic e
Groq** levantam `UnsupportedError`.

```python
from jangada_ai import LLM

emb = LLM("openai", "text-embedding-3-small")   # ou ("gemini", "gemini-embedding-001")
emb.embed("uma frase")            # -> vetor (list[float])
emb.embed(["a", "b"])             # -> lista de vetores
emb.embed(textos, task="document")  # task: "document" ao indexar, "query" ao buscar
```

`task` vira `task_type` no Gemini (`RETRIEVAL_DOCUMENT`/`RETRIEVAL_QUERY`); a
OpenAI ignora. `dimensions` (OpenAI) / `output_dimensionality` (Gemini) vão via `**opts`.

| Provider | Embeddings? | Modelo típico |
|----------|:-----------:|---------------|
| OpenAI   | ✅ | `text-embedding-3-small` / `-large` |
| Gemini   | ✅ | `gemini-embedding-001` |
| Anthropic| ❌ | — (use Voyage/Cohere por fora) |
| Groq     | ❌ | — |

## Pipeline completo (`RAG`)

```python
from jangada_ai import LLM
from jangada_ai.rag import RAG, vector_store

emb  = LLM("openai", "text-embedding-3-small")
chat = LLM("openai", "gpt-4o-mini")

# o store é escolhido pela STRING DE CONEXÃO (só passe a sua DATABASE_URL_VECTOR)
store = vector_store("postgresql://user:senha@host:5432/db")   # ou "mongodb+srv://..."
rag = RAG(emb, store, chat=chat, k=5)   # k = nº de trechos no contexto (ajustável)

rag.add_document("manual.pdf", metadata={"fonte": "manual"})   # extrai -> chunk -> embed -> grava
resposta = rag.ask("Como faço backup?", mode="hybrid")          # usa o k do RAG
mais = rag.ask("Como faço backup?", k=10, mode="hybrid")        # override por chamada
print(resposta.text)
for s in resposta.sources:
    print(s.score, s.chunk.content[:80])
```

## Vector store por string de conexão

`vector_store(url)` detecta o adapter pelo esquema:

| URL | Adapter | Busca |
|-----|---------|-------|
| `postgresql://` / `postgres://` | pgvector (Postgres) | cosseno (`<=>`) + full-text (`tsvector`) |
| `mongodb://` / `mongodb+srv://` | MongoDB | Atlas `$vectorSearch` + `$text` (fallback cosseno client-side) |
| `memory` / `None` | em memória | cosseno + keyword (sem deps) |

As tabelas/coleções e índices são criados sozinhos no primeiro uso (`setup`).

### Busca textual em português (pgvector)

O `PgVectorStore` usa a configuração `'simple'` do Postgres por padrão (sem
stemming nem stopwords). Para conteúdo em **português**, passe
`text_config="portuguese"` — melhora a parte lexical da busca híbrida (stemming PT
+ stopwords):

```python
from jangada_ai.rag import vector_store

store = vector_store("postgresql://...", text_config="portuguese")
```

A config é fixada na **criação** da tabela (a coluna `tsv` é GENERATED), então
defina-a antes do primeiro `setup`. Vale qualquer `regconfig` do Postgres
(`english`, `spanish`, ...).

## Modos de busca

`mode="vector" | "text" | "hybrid"`:

- **vector** — só similaridade do embedding.
- **text** — lexical: **BM25** no store em memória (com `rank_bm25`; cai para
  contagem de termos sem ele) e full-text nativo no pgvector (`tsvector`) / Mongo (`$text`).
- **hybrid** — combina os dois por **Reciprocal Rank Fusion (RRF)**.

O balanço vetorial × lexical sai de `weights=(vetorial, texto)` ou do atalho
**`alpha`** (0 = só BM25/texto, 1 = só vetorial; `alpha` vira `weights=(alpha, 1-alpha)`):

```python
RAG(emb, store, chat=chat, alpha=0.5)   # equilíbrio; 0.0 = só BM25, 1.0 = só vetorial
```

```python
rag.search("backup incremental", k=5, mode="vector")   # só vetorial
rag.search("backup incremental", k=5, mode="hybrid")   # vetorial + texto (RRF)
```

## Reranking (maior salto de qualidade)

O retriever traz candidatos (bom *recall*), mas a ordem nem sempre é a melhor.
Um **reranker** — modelo treinado em "este trecho responde a esta pergunta?" —
reordena os candidatos e fica com os melhores. Em RAG é o maior ganho de
qualidade por esforço.

Com `reranker=`, o `RAG` busca **mais** candidatos (`fetch_k`, padrão `k*4`) e
reordena, devolvendo os `k` melhores:

```python
from jangada_ai.rag import RAG, Reranker, vector_store

rag = RAG(emb, vector_store("memory"), chat=chat, reranker=Reranker.cohere())
rag.ask("Como faço backup incremental?")   # busca k*4 e reordena para os k melhores
```

Construtores do `Reranker`:

- `Reranker.cohere(model="rerank-v3.5")` — Cohere Rerank (precisa de `cohere` e
  `COHERE_API_KEY`).
- `Reranker.voyage(model="rerank-2.5")` — Voyage Rerank (precisa de `voyageai` e
  `VOYAGE_API_KEY`).
- `Reranker.fn(lambda query, docs: [scores])` — qualquer scorer (ex.: um
  cross-encoder local ou um LLM seu).

Extra opcional: `pip install "jangada-ai[rerank]"`. Controle fino:
`RAG(..., reranker=..., fetch_k=40)`; por chamada, `rag.search(q, rerank=False)`
desliga e `rerank=OutroReranker` sobrescreve.

## Parâmetros ajustáveis

Definidos no `RAG(...)` (padrão) e/ou por chamada:

```python
rag = RAG(
    emb, store, chat=chat,
    k=5,                      # nº de trechos no contexto
    min_score=0.25,           # descarta trechos abaixo dessa similaridade
    max_context_chars=6000,   # orçamento do contexto (trunca o excedente)
    chunker=meu_chunker,      # função(text)->list[str] (troca o chunking padrão)
    rrf_k=60,                 # constante do RRF (híbrido)
    weights=(1.0, 0.5),       # pesos (vetorial, texto) no híbrido
    chunk_size=1000, overlap=200,
)

# filtro por metadata (escopar por documento/fonte/tenant) + override por chamada
rag.ask("backup?", k=8, filter={"fonte": "manual"}, min_score=0.3, mode="hybrid")
rag.search("backup?", filter={"tenant": "acme"}, mode="vector")
```

- **`filter`** vira `metadata @> ...` no pgvector e `$match` em `metadata.<chave>` no Mongo.
- **`min_score`** usa a similaridade real (cosseno no vetorial, rank no texto).
- **`max_context_chars`** corta os trechos que não couberem (mantém ao menos um).
- **`weights=(v, t)`** pondera os rankings vetorial e de texto na fusão RRF.

## Estratégias avançadas de retrieval (opt-in)

Passe `strategy=` no `search`/`ask`. Padrão: busca simples (continua igual).

- **multi-query** — o LLM gera variações da pergunta, busca todas e funde por RRF
  (pega sinônimos/ângulos). `rag.ask(q, strategy="multi_query")`.
- **parent-document** — indexe filhos pequenos (precisos) guardando o trecho-pai
  grande; a busca devolve o pai (melhor contexto):
  ```python
  rag.add_document("manual.pdf", parent_chunk_size=4000)   # filhos + pai
  rag.ask("Como faço X?", strategy="parent_document")
  ```
- **contextual compression** — após buscar, o LLM extrai de cada trecho só o
  relevante (encolhe o contexto/custo): `rag.ask(q, compress=True)`.

Combinam entre si e com o `reranker=`.

## Indexação incremental

`sync_document`/`sync_texts` reindexam **só o que mudou** (dedup por hash do
conteúdo): embeda os chunks novos e remove os que sumiram. Requer `document_id`
e um store com suporte (memória hoje; pgvector/Mongo: usar `add_*`).

```python
rag.sync_document("manual.pdf", name="manual")
# {'added': 3, 'removed': 1, 'unchanged': 42}  -> só os 3 novos foram embedados
```

## Qual recurso usar? (resumo)

Todos são **opt-in** — a lib funciona sem nenhum. Some-os conforme a necessidade:

| Quero… | Use | Custo extra |
|--------|-----|-------------|
| Melhorar muito a ordem dos trechos | `reranker=Reranker.cohere()` | 1 chamada de rerank |
| Pegar sinônimos/perguntas vagas | `strategy="multi_query"` | N buscas + 1 LLM |
| Contexto melhor sem perder precisão | `parent_chunk_size=` + `strategy="parent_document"` | — |
| Reduzir tokens de contexto | `compress=True` | 1 LLM por trecho |
| Chunks que não cortam ideias | `chunker=semantic_chunker(emb)` | embeddings no índice |
| Reindexar barato (só o que mudou) | `sync_document(...)` | — |

Receita recomendada para produção: **semantic chunking** (índice) +
**reranker** (busca). Acrescente **multi-query** se as perguntas forem vagas.

Exemplo combinando tudo:

```python
from jangada_ai import LLM
from jangada_ai.rag import RAG, Reranker, semantic_chunker, vector_store

emb = LLM("openai", "text-embedding-3-small")
rag = RAG(
    emb, vector_store("postgresql://..."), chat=LLM("openai", "gpt-4o-mini"),
    chunker=semantic_chunker(emb),     # índice por assunto
    reranker=Reranker.cohere(),        # ordem por relevância
)
rag.sync_document("manual.pdf", name="manual")          # incremental
ans = rag.ask("Como faço backup?", strategy="multi_query", compress=True)
```

POC executável com todos os recursos lado a lado:
[`pocs/rag-advanced-poc`](https://github.com/nerigleston/jangada).

## Chunking

```python
from jangada_ai.rag import chunk_text, semantic_chunker
chunk_text(texto, size=1000, overlap=200)        # padrão: tamanho fixo, sem cortar palavras

# semantic chunking (opt-in): quebra por similaridade, não por tamanho
RAG(emb, store, chunker=semantic_chunker(emb))   # frases do mesmo assunto ficam juntas
```

Relacionado: [Documentos](documents.md) (extração de texto reaproveitada no RAG)
e [Observabilidade](observability.md).

## Exemplo

[`examples/rag_example.py`](https://raw.githubusercontent.com/nerigleston/jangada-docs/main/examples/rag_example.py) — script executável.
