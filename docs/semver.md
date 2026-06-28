# Versionamento e estabilidade

A jangada segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/)
(`MAJOR.MINOR.PATCH`), com as ressalvas da fase `0.x` descritas abaixo. As
mudanças por versão ficam no [CHANGELOG.md](../CHANGELOG.md).

## Regras por fase

### Fase `0.x` (atual)

Enquanto a versão for `0.x`, a API ainda **pode** mudar de forma incompatível —
mas com cuidado e aviso. A convenção que seguimos nesta fase:

- **`0.X.0` (minor)** — funcionalidades novas e, quando necessário, mudanças
  incompatíveis (sempre documentadas no CHANGELOG e, quando dá, com um ciclo de
  `DeprecationWarning` antes).
- **`0.x.Y` (patch)** — correções de bug e melhorias sem quebra de API.

Na prática, a maioria das releases `0.x` adiciona recursos sem quebrar nada. O
núcleo (`LLM`, `Message`, `Completion`, `Flow`, `parse`/`complete`/`stream`) é
estável há várias versões.

### Fase `1.0+` (após o release estável)

A partir do `1.0.0`, SemVer pleno e compromisso de estabilidade da API pública:

- **`MAJOR`** (`2.0.0`) — mudanças incompatíveis na API pública.
- **`MINOR`** (`1.X.0`) — funcionalidades novas **retrocompatíveis**.
- **`PATCH`** (`1.0.Y`) — correções retrocompatíveis.

Nada de breaking change em `minor`/`patch` depois do `1.0`.

## O que conta como "breaking" (mudança incompatível)

- Remover ou renomear um símbolo da [API pública](estabilidade.md) (`__all__`).
- Mudar a assinatura de um método público de forma incompatível (remover/renomear
  parâmetro, mudar a ordem de posicionais, mudar o tipo de retorno).
- Mudar o comportamento padrão de forma observável (ex.: trocar o conjunto
  `DEFAULT_FAILOVER`, mudar o tipo de erro levantado em um caso comum).
- Mudar o shape dos tipos normalizados (`Message`, `Completion`) na fronteira.

## O que **não** conta como breaking

- Adicionar um provider, parâmetro opcional (com default), método ou módulo.
- Mudar detalhes internos dos adapters, `raw`, mensagens de erro (texto), ou a
  tabela de preços aproximada (`pricing.py`).
- Marcar algo como **experimental** (veja [estabilidade](estabilidade.md)) —
  símbolos experimentais podem mudar em qualquer release.

## Política de deprecação

Antes de remover ou mudar algo da API estável de forma incompatível:

1. **Avisamos pelo menos 1 minor antes.** O símbolo passa a emitir um
   `DeprecationWarning` (com a alternativa recomendada) e continua funcionando.
2. O aviso fica documentado no CHANGELOG (seção `Deprecated`).
3. Só na release seguinte (no mínimo) o símbolo é removido/alterado — listado em
   `Removed`/`Changed`.

```python
import warnings

warnings.warn(
    "`foo` está obsoleto desde 0.40 e será removido em 0.41; use `bar`.",
    DeprecationWarning,
    stacklevel=2,
)
```

Recursos marcados como **experimental** ([estabilidade](estabilidade.md)) estão
fora dessa garantia — podem mudar sem o ciclo de deprecação.
