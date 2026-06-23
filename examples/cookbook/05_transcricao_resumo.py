"""Transcrição + resumo encadeados: áudio -> texto -> resumo.

Caso real: uma reunião gravada vira ata. Passo 1 transcreve (Groq whisper, rápido
e barato); passo 2 resume (qualquer chat). Mostra dois providers cooperando numa
mesma pipeline simples.

Rode:
    pip install "jangada-ai[groq,openai]"
    export GROQ_API_KEY=gsk_...  OPENAI_API_KEY=sk-...
    python examples/cookbook/05_transcricao_resumo.py /caminho/reuniao.m4a
"""
from __future__ import annotations

import sys

from jangada_ai import LLM


def main(caminho: str) -> None:
    # 1) transcrição (STT) — Groq whisper
    stt = LLM("groq", "whisper-large-v3-turbo")
    texto = stt.transcribe(caminho).text
    print(f"[transcrição: {len(texto)} caracteres]\n")

    # 2) resumo — qualquer chat; template {{ }} injeta a transcrição
    chat = LLM("openai", "gpt-4o-mini")
    resumo = chat.complete(
        "Resuma em até 5 bullets os pontos principais desta transcrição:\n\n{{texto}}",
        texto=texto,
    ).text
    print("RESUMO\n------")
    print(resumo)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python 05_transcricao_resumo.py /caminho/audio.m4a")
        sys.exit(1)
    main(sys.argv[1])
