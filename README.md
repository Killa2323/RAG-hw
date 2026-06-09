# Business News RAG

Учебный **RAG** по деловым и экономическим новостям Gazeta.ru: TF-IDF + ответ с источниками.
Pipeline: новости → чанки → индекс → поиск → ответ с источниками.

**Документы:** [doc/tasklist.md](doc/tasklist.md) · **Данные:** [doc/DATA.md](doc/DATA.md) · **Улучшения:** [IMPROVEMENTS.md](IMPROVEMENTS.md) · **Датасет:** [IlyaGusev/gazeta](https://huggingface.co/datasets/IlyaGusev/gazeta)

## Требования

- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

## Быстрый старт

```bash
# 1. Окружение
uv venv
uv sync

# 2. Сборка индекса (ingest + chunk + TF-IDF)
uv run python scripts/build_index.py

# 3. Запуск UI
uv run streamlit run app/main.py
```

Откройте в браузере: http://localhost:8501

> `datasets.json` уже в репозитории — для запуска скачивать данные не нужно.
> Пересобрать корпус с нуля: `uv sync --extra data && uv run python scripts/prepare_datasets.py`.

## Данные

- **Источник:** датасет [`IlyaGusev/gazeta`](https://huggingface.co/datasets/IlyaGusev/gazeta) (новости Gazeta.ru), HuggingFace, без авторизации.
- **Корпус:** 1500 статей деловых рубрик (`business`, `financial`, `realty`, `techzone`) → ~11 000 чанков.
- Подробно — [doc/DATA.md](doc/DATA.md).

## Demo-вопросы

В sidebar приложения или в поле ввода:

| Вопрос | Ожидание |
|--------|----------|
| **инфляция и рост тарифов** | ответ, `doc_id=0` («Тарифы инфляцию не остановят»), score ≈ 0.38 |
| **курс рубля и доллар** | ответ, `doc_id=335` («Доллар обмякнет»), score ≈ 0.38 |
| **Центробанк ставка рефинансирования** | ответ, `doc_id=1` («Греф задирает ставку»), score ≈ 0.33 |
| **Как приготовить борщ?** | **отказ** — таких тем в корпусе нет (score = 0.00) |

### Реальный вывод (лог `scripts/check_generator.py`)

```
--- Есть контекст: «инфляция и рост тарифов» ---
Ответ:
На основании найденных фрагментов новостей:

[1] [financial] Тарифы инфляцию не остановят
doc_id=0, score=0.38
...тормозя рост тарифов, правительство дает экономике возможность вздохнуть,
снижает нагрузку на граждан, а значит, сдерживает инфляцию. Сейчас в России
самая низкая за последние 20 лет инфляция — 3,5% за первые четыре месяца...
Источников: 5
  [1] doc_id=0,    score=0.3828, name=[financial] Тарифы инфляцию не остановят
  [2] doc_id=435,  score=0.2469, name=[financial] Рост не гарантирован
  [3] doc_id=1251, score=0.2132, name=[business] Тариф «Предвыборный»

--- Есть контекст: «курс рубля и доллар» ---
[1] [financial] Доллар обмякнет — doc_id=335, score=0.38
  [2] doc_id=1100, score=0.3511, name=[financial] Рубль вырос на полгода
  [3] doc_id=1375, score=0.3063, name=[financial] 24 рубля за доллар

--- Есть контекст: «Центробанк ставка рефинансирования» ---
[1] [financial] Греф задирает ставку — doc_id=1, score=0.33
  «...Центробанк уже в 14-й раз с апреля прошлого года снижает ставку
   рефинансирования. С 1 июня 2010 года она уменьшена на 0,25%, до 7,75%...»

--- Negative: «Как приготовить борщ?» ---
Ответ:
В новостной базе не найдено релевантных фрагментов. Ответить по имеющимся данным невозможно.
Источников: 5 (все score = 0.0000)
```

## Скриншоты

Скриншоты Streamlit-интерфейса — в папке [doc/screenshots/](doc/screenshots/).
Чтобы получить свои: запустите `uv run streamlit run app/main.py`, задайте demo-вопрос
и сохраните скриншот страницы (виден вопрос, найденные фрагменты с `doc_id`/score и ответ).

## Проверка из консоли

```bash
uv run pytest tests/ -v                       # 11 тестов
uv run python scripts/check_retrieval.py      # top-k + score
uv run python scripts/check_generator.py      # ответы + отказ
```

## Структура проекта

```
business-news-rag/
├── app/
│   ├── config.py       # пути, top_k, размер чанка, стоп-слова
│   ├── chunker.py      # нарезка текста на чанки
│   ├── retriever.py    # TF-IDF + cosine top-k
│   ├── generator.py    # demo-ответ + отказ
│   ├── prompts.py      # system-правила, тексты отказа, порог
│   └── main.py         # Streamlit UI (top-k, порог, подсветка)
├── scripts/
│   ├── prepare_datasets.py   # Gazeta → datasets.json (нужен extra `data`)
│   ├── ingest.py             # datasets.json → documents.jsonl
│   ├── build_index.py        # ingest + chunk + TF-IDF fit
│   ├── check_retrieval.py
│   └── check_generator.py
├── data/
│   ├── raw/datasets.json     # 1500 статей (в репозитории)
│   ├── processed/            # documents.jsonl, chunks.jsonl (генерируются)
│   └── index/                # vectorizer.pkl, matrix.npz (генерируются)
├── tests/
└── doc/
```

## Как это работает (шаги pipeline)

1. **prepare_datasets** — стримит Gazeta, фильтрует деловые рубрики → `datasets.json`.
2. **ingest** — чистит текст, добавляет метаданные → `documents.jsonl`.
3. **chunking** — режет статьи на фрагменты ≤600 символов с overlap 100 → `chunks.jsonl`.
4. **index** — TF-IDF (биграммы + русские стоп-слова) → `vectorizer.pkl` + `matrix.npz`.
5. **retrieval** — cosine similarity запроса с чанками, top-k с score.
6. **generation** — ответ собирается из найденных фрагментов; при score ниже порога — **отказ**.

## Ограничения MVP

- Поиск по **словам** (TF-IDF), не по смыслу — синонимы могут не находиться.
- Demo-режим: ответ из найденных чанков, без внешней LLM.
- Индексируется только текст статей; метаданные — для источников.

См. направления развития в [IMPROVEMENTS.md](IMPROVEMENTS.md).
