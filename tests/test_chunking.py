from app.rag.ingestion import fixed_chunk, hierarchical_chunk, semantic_like_chunk


def test_fixed_chunk_splits_text() -> None:
    text = "A" * 1500
    chunks = fixed_chunk(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 3
    assert all(chunks)


def test_semantic_chunk_groups_sentences() -> None:
    text = "One. Two. Three. Four. Five. Six."
    chunks = semantic_like_chunk(text, max_sentences=2)
    assert len(chunks) == 3
    assert chunks[0].endswith(".")


def test_hierarchical_chunk_by_sections() -> None:
    text = "## Alpha\nHello\n## Beta\nWorld"
    chunks = hierarchical_chunk(text)
    assert len(chunks) == 2
