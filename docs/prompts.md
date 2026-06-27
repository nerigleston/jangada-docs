# Prompt registry (versionamento de prompts)

Versione seus prompts num lugar central — com **histórico, rollback sem deploy e
rastreabilidade** — e referencie-os **pelo nome**. É **opt-in**: convive com
prompt no código (quem não usa, ignora; nada quebra).

```python
from jangada_ai import LLM, PromptVersion
```

Usa a mesma config da [observabilidade](observability.md) (chave do projeto):

```bash
JANGADA_OBSERVABILITY_API_KEY=lobs_xxx
# opcional: JANGADA_OBSERVABILITY_ENDPOINT=https://api.jangada.dev.br
```

## As duas formas convivem

**Prompt no código (padrão, continua igual):**

```python
LLM("openai", "gpt-4o-mini").complete("Você é um assistente fiscal. ...")
```

**Prompt do registry (opt-in):**

```python
p = PromptVersion.pull("assistente-fiscal")          # versão de produção
LLM("openai", "gpt-4o-mini").complete(p.render(cliente="ACME"))
```

No fim, o registry resolve para **uma string** que entra no `complete()`/`parse()`
normal — compatível com templates `{{ }}`, structured output, tools, etc.

## Publicar uma versão (`push`)

Cada `push` cria uma **nova versão imutável**. Com `tag="production"`, marca essa
versão como a de produção (movendo a tag das anteriores).

```python
PromptVersion.push(
    "assistente-fiscal",
    "Você é um assistente fiscal. Responda sobre {{ tema }} de forma objetiva.",
    tag="production",
)
```

Também dá para criar/versionar **pelo painel** (aba *Prompts*) — as duas vias
gravam no mesmo registro.

## Resolver uma versão (`pull`)

`pull` decide qual versão usar, nesta ordem:

1. a `tag` que você pedir (`PromptVersion.pull("nome", tag="staging")`);
2. senão, a marcada como **`production`**;
3. senão, a **versão mais nova**.

```python
p = PromptVersion.pull("assistente-fiscal")   # produção (ou a mais nova)
print(p.version, p.tag)
texto = p.render(tema="ICMS")                  # aplica o template {{ }}
```

## Rollback

No painel (aba *Prompts* → o prompt → **Tornar produção** numa versão anterior),
a tag `production` volta para aquela versão — **sem deploy**. O próximo `pull`
já pega a versão restaurada.

## Rastrear no trace ("qual prompt gerou isso?")

Envolva as chamadas em `with p.use():` — cada trace registra qual **prompt e
versão** o gerou (aparece no painel, no detalhe da chamada, com link para o
prompt).

```python
p = PromptVersion.pull("assistente-fiscal")
with p.use():
    resp = llm.complete(p.render(tema="ICMS"))   # o trace sabe: assistente-fiscal v2
```

É opt-in: sem o `with`, nada muda. Precisa da observabilidade ligada
(`JANGADA_OBSERVABILITY=true`).

## Por que usar

- **Histórico + rollback** sem mexer no código nem fazer deploy.
- **Rastreabilidade**: o time vê qual versão está em produção.
- **Comparação por [evals](eval.md)**: rode o mesmo dataset com o prompt v2 vs v3
  e veja qual acerta mais.
- **Autonomia**: produto ajusta o prompt no painel; o dev não vira gargalo.

## Ver também

- [Observabilidade](observability.md) — a mesma config (chave do projeto).
- [Avaliação (evals)](eval.md) — para comparar versões de prompt por qualidade.
