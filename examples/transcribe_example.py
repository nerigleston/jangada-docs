"""Transcrição de áudio (speech-to-text).

Suportado em OpenAI, Groq e Gemini. Anthropic não aceita áudio na API.
"""
from jangada_ai import LLM, Audio

# OpenAI — endpoint dedicado
oa = LLM("openai", "gpt-4o-transcribe")
print(oa.transcribe("entrevista.mp3").text)

# Groq — rápido e barato
gq = LLM("groq", "whisper-large-v3-turbo")
print(gq.transcribe("entrevista.mp3", language="pt").text)

# Gemini — multimodal (prompt= dá instruções extras, ex.: timestamps)
gm = LLM("gemini", "gemini-2.5-flash")
print(gm.transcribe("entrevista.mp3", prompt="Transcreva com marcações de tempo.").text)

# Bytes em memória + fallback entre providers de áudio
blob = open("fala.wav", "rb").read()
stt = LLM("groq", "whisper-large-v3-turbo").with_fallback(LLM("openai", "gpt-4o-transcribe"))
print(stt.transcribe(Audio.from_bytes(blob, "audio/wav", name="fala.wav")).text)
