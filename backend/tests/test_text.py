from intel.rag.bm25 import BM25
from intel.rag.text import find_quote, split_passages


def test_find_quote_exact_and_whitespace_tolerant():
    passage = "Sales rose by 7.1% in 2024 and\n 6.4% in 2025, following 7.8% in 2023."
    assert find_quote(passage, "rose by 7.1% in 2024") == (6, 26)
    start, end = find_quote(passage, "and 6.4% in 2025")
    assert passage[start:end].split() == ["and", "6.4%", "in", "2025"]


def test_find_quote_rejects_paraphrase_and_tiny_quotes():
    passage = "Sales rose by 7.1% in 2024."
    assert find_quote(passage, "Sales increased by 7.1% in 2024") is None
    assert find_quote(passage, "7.1%") is None


def test_split_passages_respects_target_and_keeps_text():
    text = ("Sentence number one is here. " * 80) + "\n\nShort paragraph."
    parts = split_passages(text, target=300, overlap=50)
    assert all(len(p) <= 600 for p in parts)
    assert "Short paragraph." in parts[-1]


def test_bm25_ranks_relevant_passage_first():
    docs = ["footwear sales grew in the uk", "weather was mild in spring", "uk footwear market size and sales growth"]
    top = BM25(docs).top("uk footwear sales growth", 2)
    assert {i for i, _ in top} == {0, 2}
