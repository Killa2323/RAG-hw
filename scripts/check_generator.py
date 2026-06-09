"""Проверка demo-ответа: вопрос -> ответ + источники."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.generator import ask


def show(label: str, question: str) -> None:
    print(f"\n--- {label}: «{question}» ---")
    result = ask(question)
    print(f"Ответ:\n{result['answer'][:600]}\n")
    print(f"Источников: {len(result['sources'])}")
    for i, src in enumerate(result["sources"], 1):
        print(f"  [{i}] doc_id={src['doc_id']}, score={src['score']:.4f}, name={src['name'][:55]}")


if __name__ == "__main__":
    show("Есть контекст", "инфляция и рост тарифов")
    show("Есть контекст", "курс рубля и доллар")
    show("Есть контекст", "Центробанк ставка рефинансирования")
    show("Negative", "Как приготовить борщ?")
