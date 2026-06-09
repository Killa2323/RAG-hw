"""Подготовка корпуса: HuggingFace `IlyaGusev/gazeta` → data/raw/datasets.json.

Качаем датасет новостей Gazeta.ru в потоковом режиме, оставляем только деловые
и экономические рубрики (определяются по разделу в url), формируем JSON формата
{"datasets": [{"id", "name", "text", "section", "date", "url"}]}.

Запуск (нужна доп. зависимость `datasets`):
    uv sync --extra data
    uv run python scripts/prepare_datasets.py
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import RAW_DATASETS

# Деловые / экономические рубрики Gazeta.ru
TARGET_SECTIONS = {"business", "financial", "realty", "techzone"}

MAX_ARTICLES = 1500   # сколько статей берём в корпус
MAX_SCAN = 30000      # максимум записей просмотреть в потоке (предохранитель)
MIN_TEXT_LEN = 400    # отсекаем слишком короткие заметки


def section_of(url: str) -> str:
    path = urlparse(url or "").path.strip("/")
    return path.split("/")[0] if path else ""


def clean_text(text: str) -> str:
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def collect() -> list[dict]:
    from datasets import load_dataset

    ds = load_dataset("IlyaGusev/gazeta", split="train", streaming=True)

    rows: list[dict] = []
    seen_titles: set[str] = set()
    doc_id = 0

    for scanned, row in enumerate(ds):
        if scanned >= MAX_SCAN or len(rows) >= MAX_ARTICLES:
            break

        url = row.get("url", "") or ""
        section = section_of(url)
        if section not in TARGET_SECTIONS:
            continue

        title = (row.get("title", "") or "").strip()
        text = clean_text(row.get("text", ""))
        if len(text) < MIN_TEXT_LEN or not title:
            continue
        if title in seen_titles:
            continue
        seen_titles.add(title)

        rows.append(
            {
                "id": doc_id,
                "name": f"[{section}] {title}",
                "text": text,
                "section": section,
                "date": (row.get("date", "") or "")[:10],
                "url": url,
            }
        )
        doc_id += 1

    return rows


def main() -> None:
    rows = collect()
    if not rows:
        raise SystemExit("Не удалось собрать статьи — проверьте доступ к HuggingFace.")

    RAW_DATASETS.parent.mkdir(parents=True, exist_ok=True)
    RAW_DATASETS.write_text(
        json.dumps({"datasets": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    by_section: dict[str, int] = {}
    for r in rows:
        by_section[r["section"]] = by_section.get(r["section"], 0) + 1

    print(f"Записано {len(rows)} статей -> {RAW_DATASETS}")
    print("По рубрикам:", dict(sorted(by_section.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
