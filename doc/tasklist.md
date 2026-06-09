# Tasklist — итерационный план разработки

Опирается на: [vision.md](vision.md) · [conventions.md](conventions.md) · [00_project_idea.md](00_project_idea.md) · [workflow.md](workflow.md)

**Правило:** одна итерация = один проверяемый результат.

---

## 📊 Отчёт по прогрессу

| Итерация | Название | Статус | Проверка |
|:--------:|----------|:------:|----------|
| 0 | Каркас проекта | ✅ | `uv sync` без ошибок |
| 1 | Подготовка данных | ✅ | `datasets.json`, 1500 статей |
| 2 | Ingestion | ✅ | `documents.jsonl` создан |
| 3 | Chunking | ✅ | `chunks.jsonl`, тест chunking |
| 4 | Индекс TF-IDF | ✅ | файлы в `data/index/` |
| 5 | Retrieval | ✅ | top-k + score в консоли |
| 6 | Demo-ответ + отказ | ✅ | ответ с источниками, отказ на нерелевантный вопрос |
| 7 | Streamlit UI | ✅ | 3 demo-вопроса в браузере |
| 8 | Тесты и README | ✅ | `pytest` green, README воспроизводим |
| 9 | Документ о данных | ✅ | `doc/DATA.md` |

**Готовность MVP:** 10 / 10

---

## Итерация 0 — Каркас проекта

- [x] `pyproject.toml` — зависимости: streamlit, scikit-learn, scipy, pytest; extra `data`: datasets
- [x] `.gitignore` — `.venv/`, `data/index/*`, `data/processed/*`, `__pycache__/`
- [x] Папки: `app/`, `scripts/`, `data/{raw,processed,index}/`, `tests/`, `doc/`
- [x] `app/config.py` — пути, `top_k`, размер чанка, стоп-слова

**Проверка:** `uv sync && uv run python -c "import app.config"`

---

## Итерация 1 — Подготовка данных

- [x] `scripts/prepare_datasets.py` — стрим `IlyaGusev/gazeta`, фильтр деловых рубрик
- [x] `data/raw/datasets.json` — 1500 статей, поля `id`, `name`, `text`, `section`, `date`, `url`

**Проверка:**
```bash
uv run python -c "import json; d=json.load(open('data/raw/datasets.json', encoding='utf-8')); print(len(d['datasets']))"
# → 1500
```

---

## Итерация 2 — Ingestion

- [x] `scripts/ingest.py` — JSON → `data/processed/documents.jsonl`, очистка текста, метаданные

**Проверка:** `uv run python scripts/ingest.py` → `documents.jsonl`, строк = 1500

---

## Итерация 3 — Chunking

- [x] `app/chunker.py` — нарезка по абзацам, max 600, overlap 100 → `chunks.jsonl`

**Проверка:** `uv run pytest tests/test_chunking.py -v`

---

## Итерация 4 — Индекс TF-IDF

- [x] `scripts/build_index.py` — ingest + chunk + TF-IDF (биграммы, стоп-слова, `min_df=2`)
- [x] Сохранение: `data/index/vectorizer.pkl`, `matrix.npz`, `chunks.jsonl`

**Проверка:** `uv run python scripts/build_index.py` → `Документов: 1500, чанков: 11154`

---

## Итерация 5 — Retrieval

- [x] `app/retriever.py` — загрузка индекса, cosine top-k, возврат `text`, `doc_id`, `name`, `score`

**Проверка:** `uv run python scripts/check_retrieval.py`

---

## Итерация 6 — Demo-ответ + отказ

- [x] `app/prompts.py` — system-правила, тексты отказа, `MIN_SCORE`
- [x] `app/generator.py` — ответ из top-k + источники; отказ при score ниже порога

**Проверка:** `uv run python scripts/check_generator.py` → 3 ответа + 1 отказ

---

## Итерация 7 — Streamlit UI

- [x] `app/main.py` — поле вопроса, top-k фрагменты, ответ, источники
- [x] Улучшение: ползунки top-k и порога, подсветка слов запроса
- [x] Сообщение, если индекс не собран

**Проверка:** `uv run streamlit run app/main.py`

---

## Итерация 8 — Тесты и README

- [x] `tests/test_chunking.py`, `tests/test_retrieval.py` — 11 тестов
- [x] Корневой `README.md` — uv, build_index, streamlit, demo-вопросы, скриншоты

**Проверка:** `uv run pytest tests/ -v` → 11 passed

---

## Итерация 9 — Документ о данных

- [x] `doc/DATA.md` — источник, что индексируем / не индексируем, состав корпуса, демо
- [x] Ссылка из `README.md` на `doc/DATA.md`

**Проверка:** файл существует, разделы «Источник данных», «Что индексируем», «Назначение репозитория» на месте

---

## Критерий «MVP готов»

- [x] Все итерации ✅
- [x] 3 demo-вопроса — ответ с источником; 1 negative — отказ
- [x] Путь воспроизводим: `data/raw/` → index → Streamlit
- [x] `doc/DATA.md` описывает данные и назначение репозитория
