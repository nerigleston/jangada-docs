"""Detecção de objetos via LLM (provider-agnóstica).

Funciona em qualquer provider com visão; o Gemini é o mais preciso por usar o
formato box_2d (0–1000) nativamente. As caixas voltam em pixels absolutos.
"""
from jangada_ai import LLM, detect_objects

llm = LLM("gemini", "gemini-2.5-flash")   # ou ("openai", "gpt-4o"), etc.

# 1) Detectar tudo
dets = detect_objects(llm, "foto.png")
for d in dets:
    print(f"{d.label}: {d.box}")          # [x1, y1, x2, y2] em pixels

# 2) Restringir o alvo e limitar a quantidade
gatos = detect_objects(llm, "foto.png", target="todos os gatos", max_objects=5)

# 3) Desenhar as caixas (requer Pillow: pip install pillow)
try:
    from PIL import Image, ImageDraw

    img = Image.open("foto.png")
    draw = ImageDraw.Draw(img)
    for d in dets:
        draw.rectangle(d.box, outline="red", width=3)
        draw.text((d.box[0], d.box[1] - 12), d.label, fill="red")
    img.save("foto_anotada.png")
    print("Salvo em foto_anotada.png")
except ImportError:
    print("Instale pillow para desenhar as caixas.")
