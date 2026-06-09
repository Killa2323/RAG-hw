"""Build TF-IDF index: ingest + chunk + fit + save."""

import pickle
import shutil
import sys
from pathlib import Path

import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from app.chunker import load_documents, run as chunk_run
from app.config import (
    CHUNKS_JSONL,
    DATA_INDEX,
    INDEX_CHUNKS_JSONL,
    MATRIX_NPZ,
    STOPWORDS_RU,
    VECTORIZER_PKL,
)
from ingest import run as ingest_run


def build_tfidf(texts: list[str]) -> tuple[TfidfVectorizer, scipy.sparse.csr_matrix]:
    # ngram_range=(1,2) — учитываем биграммы, чуть лучше ловит фразы в новостях;
    # stop_words — убираем русские служебные слова, иначе шумят и ломают отказ.
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        stop_words=STOPWORDS_RU,
    )
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


def save_index(
    vectorizer: TfidfVectorizer,
    matrix: scipy.sparse.csr_matrix,
    chunks_path: Path = CHUNKS_JSONL,
) -> int:
    DATA_INDEX.mkdir(parents=True, exist_ok=True)

    with VECTORIZER_PKL.open("wb") as f:
        pickle.dump(vectorizer, f)

    scipy.sparse.save_npz(MATRIX_NPZ, matrix)
    shutil.copy2(chunks_path, INDEX_CHUNKS_JSONL)
    return matrix.shape[0]


def run() -> int:
    doc_count = ingest_run()
    chunk_count = chunk_run()
    chunks = load_documents(CHUNKS_JSONL)
    texts = [c["text"] for c in chunks]

    if not texts:
        raise ValueError("Нет чанков для индексации")

    vectorizer, matrix = build_tfidf(texts)
    save_index(vectorizer, matrix)
    print(f"Документов: {doc_count}, чанков: {chunk_count}, матрица: {matrix.shape}")
    return chunk_count


def main() -> None:
    run()
    print(f"Индекс сохранён -> {DATA_INDEX}")


if __name__ == "__main__":
    main()
