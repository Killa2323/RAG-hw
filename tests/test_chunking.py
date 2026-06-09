"""Тесты нарезки текста на чанки."""

from app.chunker import chunk_document, chunk_text, run


def test_chunk_text_respects_max_size():
    text = "Первый абзац.\n\n" + "слово " * 300
    chunks = chunk_text(text, max_chars=600, overlap=100)
    assert chunks
    assert all(len(c) <= 600 for c in chunks)


def test_chunk_text_keeps_short_text_single():
    text = "Инфляция ускорилась.\n\nТарифы выросли на 10 процентов."
    chunks = chunk_text(text, max_chars=600, overlap=100)
    assert len(chunks) == 1
    assert "Инфляция" in chunks[0]
    assert "Тарифы" in chunks[0]


def test_chunk_text_overlap_between_chunks():
    para1 = "А" * 500
    para2 = "Б" * 500
    text = f"{para1}\n\n{para2}"
    chunks = chunk_text(text, max_chars=600, overlap=100)
    assert len(chunks) >= 2
    assert chunks[1].startswith(chunks[0][-100:])


def test_chunk_document_has_doc_id_and_metadata():
    doc = {
        "doc_id": "42",
        "name": "[business] Тестовая новость про рынок",
        "text": "Компания отчиталась о прибыли за квартал.",
    }
    chunks = chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0]["doc_id"] == "42"
    assert chunks[0]["chunk_id"] == "42_0"
    assert chunks[0]["name"].startswith("[business]")


def test_run_creates_chunks_jsonl(tmp_path):
    docs = tmp_path / "documents.jsonl"
    docs.write_text(
        '{"doc_id": "0", "name": "[financial] A", "text": "Короткая новость про банк."}\n',
        encoding="utf-8",
    )
    out = tmp_path / "chunks.jsonl"
    count = run(input_path=docs, output_path=out)
    assert count == 1
    assert out.exists()
    line = out.read_text(encoding="utf-8").strip()
    assert '"doc_id": "0"' in line
