# Vision — техническое видение проекта

> Отправная точка для разработки.
> Идея продукта: [00_project_idea.md](00_project_idea.md)

**Учебный RAG** по деловым новостям Gazeta.ru: локально, просто, с ответом и источниками.

---

## 1. Технологии

Минимальный стек — только то, без чего MVP не работает.

| Слой | Выбор | Комментарий |
|------|-------|-------------|
| Язык | **Python 3.10+** | — |
| Окружение | **uv** + `.venv` | venv через uv; локально, не коммитим |
| UI | **Streamlit** | Один entry point: видны фрагменты, scores, источники |
| Поиск | **TF-IDF + cosine similarity** (`scikit-learn`) | Без torch и тяжёлых моделей; ищет по совпадению слов |
| Индекс | **Локальные файлы** (`data/index/`) | `vectorizer.pkl` + `matrix.npz` + `chunks.jsonl` — без векторной БД и сервера |
| LLM | **Только demo-режим** | Ответ из найденных чанков по правилам system prompt; внешний API не используем |
| Данные | **`IlyaGusev/gazeta`** → `data/raw/datasets.json` | Деловые рубрики; в RAG идёт текст статьи |
| Подготовка данных | **HuggingFace `datasets`** (опционально) | Только для пересборки корпуса (`--extra data`) |
| Тесты | **pytest** | chunking, retrieval, источники, отказ |
| Зависимости | **`pyproject.toml`** + uv | `uv sync`; без pip/poetry/conda |

### Данные (как устроено)

1. `prepare_datasets.py` стримит `IlyaGusev/gazeta` с HuggingFace.
2. Фильтрует рубрики `business`, `financial`, `realty`, `techzone` (по `url`).
3. Чистит текст, дедуплицирует по заголовку, берёт 1500 статей → `datasets.json`.
4. `datasets.json` коммитится — для запуска проекта HuggingFace не нужен.

### Ограничение TF-IDF (осознанно)

Поиск по ключевым словам: синонимы и перефразировки могут не находиться. Для учебного MVP это приемлемо — pipeline тот же, что и с эмбеддингами. Чтобы служебные слова не шумели и корректно срабатывал отказ, добавлены **русские стоп-слова** и биграммы.

### Не используем в MVP

Векторные БД (Chroma/Qdrant/FAISS), sentence-transformers, torch, LangChain/LlamaIndex, FastAPI, Docker, reranking, hybrid search, внешние LLM API, pip/poetry/conda (используем **uv**).

### Окружение (как запускать)

```bash
uv venv          # создать .venv
uv sync          # установить зависимости из pyproject.toml
```
