"""Проверка retrieval — понятный вывод top-k результатов."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.retriever import Retriever


def print_hit(i: int, hit: dict) -> None:
    preview = hit["text"][:140].replace("\n", " ")
    print(f"  [{i}] doc_id={hit['doc_id']}, score={hit['score']:.4f} | {hit['name'][:60]}")
    print(f"      {preview}...")


def main() -> None:
    print("=== Проверка Retriever ===\n")

    r = Retriever()
    print(f"OK: индекс загружен, чанков: {len(r.chunks)}\n")

    queries = [
        "инфляция и рост тарифов",
        "курс рубля и доллар",
        "Центробанк ставка рефинансирования",
        "Как приготовить борщ?",
    ]

    for query in queries:
        print(f"Запрос: «{query}»")
        results = r.search(query, k=3)
        for i, hit in enumerate(results, 1):
            print_hit(i, hit)
        print()


if __name__ == "__main__":
    main()
