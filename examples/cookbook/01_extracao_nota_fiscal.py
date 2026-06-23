"""Extração de nota fiscal: foto -> dados estruturados (Pydantic).

Caso real: você fotografa um cupom/NFC-e e quer os campos num objeto validado,
não em texto solto. Uma chamada `parse()` com `images=` faz vision + structured
output de uma vez — e funciona em qualquer provider com visão (aqui, OpenAI).

Rode:
    pip install "jangada-ai[openai]"
    export OPENAI_API_KEY=sk-...
    python examples/cookbook/01_extracao_nota_fiscal.py /caminho/nota.jpg
"""
from __future__ import annotations

import sys

from pydantic import BaseModel, Field

from jangada_ai import LLM


class Item(BaseModel):
    descricao: str
    quantidade: float
    valor_unitario: float
    valor_total: float


class NotaFiscal(BaseModel):
    estabelecimento: str
    cnpj: str | None = Field(default=None, description="Só os dígitos ou no formato com pontos")
    cidade: str | None = None
    itens: list[Item]
    valor_a_pagar: float
    forma_pagamento: str | None = None


def main(caminho: str) -> None:
    llm = LLM("openai", "gpt-4o-mini")  # qualquer modelo com visão serve

    nota = llm.parse(
        "Extraia os dados desta nota fiscal. Transcreva os valores exatamente "
        "como aparecem; se um campo não existir, deixe nulo. Não invente.",
        NotaFiscal,
        images=[caminho],
    ).parsed

    print(f"\n{nota.estabelecimento}" + (f" — {nota.cidade}" if nota.cidade else ""))
    if nota.cnpj:
        print(f"CNPJ: {nota.cnpj}")
    print("-" * 40)
    for i in nota.itens:
        print(f"  {i.descricao}: {i.quantidade:g} x {i.valor_unitario:.2f} = {i.valor_total:.2f}")
    print("-" * 40)
    print(f"TOTAL A PAGAR: {nota.valor_a_pagar:.2f}"
          + (f"  ({nota.forma_pagamento})" if nota.forma_pagamento else ""))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python 01_extracao_nota_fiscal.py /caminho/nota.jpg")
        sys.exit(1)
    main(sys.argv[1])
