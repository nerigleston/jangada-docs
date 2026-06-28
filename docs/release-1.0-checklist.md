# Checklist do release 1.0

Critérios para promover a jangada de `0.x` para `1.0.0` (primeira release estável,
com compromisso de SemVer pleno — veja [semver.md](semver.md)). **Não** taggear
`v1.0.0` antes de tudo aqui estar verde.

## Pré-requisitos de processo

- [x] **B1 — CHANGELOG** no formato Keep a Changelog ([CHANGELOG.md](../CHANGELOG.md)),
  com `[Unreleased]` e histórico.
- [x] **B2 — Política de versionamento e deprecação** documentada ([semver.md](semver.md))
  + seção "Versionamento e estabilidade" no README.
- [x] **B3 — API pública vs interna** definida: `__all__` explícito em
  `jangada_ai/__init__.py` + mapa de estabilidade ([estabilidade.md](estabilidade.md)).
- [x] **B5 — CI em matriz** de Python (3.10/3.11/3.12/3.13) antes do build/publish.

## Qualidade

- [x] Suíte de testes verde no run padrão (`pytest -q`, sem integração).
- [x] Cobertura do **núcleo** (`client`/providers/`errors`/`flow`/`graph`/`message`)
  por testes com `FakeProvider`/mocks, sync **e** async.
- [ ] Smoke de integração por provider passando ao menos uma vez com credenciais
  reais (`pytest -m integration`) — inclui os providers novos (azure/bedrock/vertex).
- [ ] Revisão final da API pública: nenhum símbolo "vazando" em `__all__` que não
  queiramos congelar (mover dúvidas para **experimental** em [estabilidade.md](estabilidade.md)).

## Documentação

- [x] Uma página de docs por provider (incl. azure/bedrock/vertex) e linhas no
  `llms.txt`.
- [x] Exemplos runnable por feature/provider em `examples/`.
- [ ] Revisão de consistência docs PT/EN no site (`doc/`) e na LP — **fora deste
  repo** (ver CLAUDE.md do workspace).

## Quando tudo estiver verde

1. Bump `version = "1.0.0"` em `pyproject.toml` **e** `__version__` em
   `jangada_ai/__init__.py`.
2. Mover o bloco preparado do `[Unreleased]`/`[1.0.0]` no CHANGELOG para uma seção
   datada `[1.0.0] — AAAA-MM-DD`.
3. Commit + push, depois a tag (dispara o publish no PyPI):

   ```bash
   git commit -am "release: v1.0.0"
   git push
   git tag v1.0.0 && git push origin v1.0.0
   ```

> A decisão de promover para 1.0 é do mantenedor — este checklist é o gate, não
> um gatilho automático.
