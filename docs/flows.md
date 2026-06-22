# Fluxos e orquestração (Flow e Graph)

A jangada traz duas formas de encadear chamadas, ambas agregando `usage`/`cost`.

## Flow — sequencial

`Flow` encadeia `Step`s: a saída de um vira entrada do próximo.

```python
from jangada_ai import LLM, Flow, Step

llm = LLM("openai", "gpt-4o-mini")

flow = Flow([
    Step("rascunho", "Escreva um parágrafo sobre {{tema}}."),
    Step("revisao",  "Revise e melhore:\n{{rascunho}}"),
])

resultado = flow.run(llm, tema="jangadas do Nordeste")
print(resultado.output)     # saída do último step
print(resultado.cost)       # custo agregado de toda a cadeia
```

Cada `Step` referencia as saídas anteriores pelo nome via template `{{ }}`.

## Graph — roteamento condicional + paralelo

`Graph` permite ramificar (roteamento condicional) e executar nós em paralelo
(core async), juntando os resultados.

```python
from jangada_ai import Graph

# roteamento condicional: escolhe o próximo nó conforme a saída
# paralelo + junção: dispara vários nós e combina as respostas
g = Graph()
# ... defina nós, arestas condicionais e junções ...
res = g.run(...)        # GraphResult agrega usage/cost
```

Veja os exemplos executáveis em
os exemplos do pacote (`examples/graph_example.py`).

## Custo agregado

`FlowResult` e `GraphResult` somam `usage` e `cost` de todas as etapas — útil
para observabilidade. Detalhes em [Custo e tokens](cost.md) e, para inspecionar
passo a passo, [Debug](debug.md).
