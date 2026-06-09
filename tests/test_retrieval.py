"""Тесты retrieval и demo-ответа на изолированном мини-индексе."""

import json
import pickle
from pathlib import Path

import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import TOP_K
from app.generator import ask
from app.prompts import REFUSAL_NO_CONTEXT
from app.retriever import Retriever

import pytest


@pytest.fixture
def mini_index(tmp_path: Path) -> dict[str, Path]:
    """Мини-индекс из двух новостных чанков для изолированных тестов."""
    chunks = [
        {
            "chunk_id": "2_0",
            "doc_id": "2",
            "name": "[financial] Инфляция и рост тарифов",
            "text": "Инфляция ускорилась, тарифы на услуги ЖКХ выросли. Центробанк отреагировал ставкой.",
        },
        {
            "chunk_id": "1_0",
            "doc_id": "1",
            "name": "[business] Продажи автомобилей",
            "text": "Продажи новых автомобилей выросли, дилеры отчитались о высоком спросе на рынке.",
        },
    ]
    chunks_path = tmp_path / "chunks.jsonl"
    with chunks_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform(texts)

    vectorizer_path = tmp_path / "vectorizer.pkl"
    matrix_path = tmp_path / "matrix.npz"
    with vectorizer_path.open("wb") as f:
        pickle.dump(vectorizer, f)
    scipy.sparse.save_npz(matrix_path, matrix)

    return {
        "vectorizer_path": vectorizer_path,
        "matrix_path": matrix_path,
        "chunks_path": chunks_path,
    }


def test_search_returns_k_results(mini_index):
    r = Retriever(**mini_index)
    results = r.search("инфляция тарифы", k=2)
    assert len(results) == 2


def test_search_results_have_doc_id_and_score(mini_index):
    r = Retriever(**mini_index)
    results = r.search("инфляция", k=TOP_K)
    assert results
    for hit in results:
        assert "doc_id" in hit
        assert "text" in hit
        assert "score" in hit
        assert "name" in hit
        assert isinstance(hit["score"], float)


def test_search_inflation_prefers_financial_doc(mini_index):
    r = Retriever(**mini_index)
    results = r.search("инфляция тарифы ставка", k=1)
    assert results[0]["doc_id"] == "2"
    assert results[0]["score"] > 0


def test_search_empty_query_returns_empty(mini_index):
    r = Retriever(**mini_index)
    assert r.search("") == []
    assert r.search("   ") == []


def test_ask_sources_contain_doc_id(mini_index):
    result = ask("инфляция тарифы", retriever=Retriever(**mini_index))
    assert result["sources"]
    assert all("doc_id" in src for src in result["sources"])
    assert result["sources"][0]["doc_id"] == "2"


def test_ask_refuses_without_relevant_context(mini_index):
    result = ask("Как приготовить борщ?", retriever=Retriever(**mini_index))
    assert result["answer"] == REFUSAL_NO_CONTEXT
