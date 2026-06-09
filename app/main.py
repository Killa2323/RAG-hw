"""Streamlit UI: вопрос -> фрагменты -> ответ -> источники.

Улучшение над базовым MVP (см. IMPROVEMENTS.md, п. «Интерфейс»):
- регулируемый порог релевантности (score) и число результатов top-k;
- подсветка слов запроса в найденных фрагментах.
"""

import html
import re

import streamlit as st

from app.config import INDEX_CHUNKS_JSONL, MATRIX_NPZ, TOP_K, VECTORIZER_PKL
from app.generator import ask
from app.prompts import MIN_SCORE
from app.retriever import Retriever

DEMO_QUESTIONS = [
    "инфляция и рост тарифов",
    "курс рубля и доллар",
    "Центробанк ставка рефинансирования",
    "Как приготовить борщ?",
]


def index_exists() -> bool:
    return all(p.exists() for p in (VECTORIZER_PKL, MATRIX_NPZ, INDEX_CHUNKS_JSONL))


@st.cache_resource
def load_retriever() -> Retriever:
    return Retriever()


def highlight(text: str, query: str) -> str:
    """Подсвечивает слова запроса (длиннее 2 символов) в тексте фрагмента."""
    safe = html.escape(text)
    terms = sorted(
        {t for t in re.findall(r"\w{3,}", query, flags=re.UNICODE)},
        key=len,
        reverse=True,
    )
    for term in terms:
        safe = re.sub(
            f"({re.escape(html.escape(term))})",
            r"<mark>\1</mark>",
            safe,
            flags=re.IGNORECASE | re.UNICODE,
        )
    return safe.replace("\n", "<br>")


def render_chunk(i: int, src: dict, query: str, expanded: bool) -> None:
    label = f"[{i}] doc_id={src['doc_id']} · score={src['score']:.4f}"
    with st.expander(label, expanded=expanded):
        st.markdown(f"**{src['name']}**")
        st.markdown(highlight(src["text"], query), unsafe_allow_html=True)


def render_fragments(sources: list[dict], query: str, min_score: float) -> None:
    st.subheader("Найденные фрагменты (top-k)")
    if not sources:
        st.info("Фрагменты не найдены.")
        return
    for i, src in enumerate(sources, 1):
        render_chunk(i, src, query, expanded=src["score"] >= min_score)


def render_sources(sources: list[dict], query: str) -> None:
    st.subheader("Источники")
    if not sources:
        st.info("Источники отсутствуют.")
        return
    for i, src in enumerate(sources, 1):
        render_chunk(i, src, query, expanded=False)


def main() -> None:
    st.set_page_config(page_title="Business News RAG", layout="wide")
    st.title("Business News RAG")
    st.caption("Учебный RAG по деловым и экономическим новостям: TF-IDF + ответ с источниками")

    if not index_exists():
        st.error(
            "Индекс не собран. Сначала выполните:\n\n"
            "`uv run python scripts/build_index.py`"
        )
        st.stop()

    st.sidebar.header("Параметры поиска")
    top_k = st.sidebar.slider("Сколько фрагментов (top-k)", 1, 10, TOP_K)
    min_score = st.sidebar.slider(
        "Порог релевантности (score)", 0.0, 0.5, float(MIN_SCORE), 0.01
    )

    st.sidebar.header("Demo-вопросы")
    for q in DEMO_QUESTIONS:
        if st.sidebar.button(q, use_container_width=True):
            st.session_state["question"] = q

    question = st.text_input("Ваш вопрос", key="question")

    if st.button("Спросить", type="primary"):
        if not question.strip():
            st.warning("Введите вопрос.")
            st.stop()

        with st.spinner("Поиск..."):
            result = ask(
                question.strip(),
                k=top_k,
                retriever=load_retriever(),
                min_score=min_score,
            )

        render_fragments(result["sources"], question, min_score)

        st.subheader("Ответ")
        st.text(result["answer"])

        render_sources(result["sources"], question)


if __name__ == "__main__":
    main()
