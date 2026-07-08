"""Tests for sentence-transformers text embedding."""

from services.embedder import embed_texts


def test_embed_texts_returns_one_vector_per_input():
    vectors = embed_texts(["hello world", "another sentence"])

    assert len(vectors) == 2
    assert len(vectors[0]) == len(vectors[1])
    assert len(vectors[0]) > 0


def test_embed_texts_empty_input_returns_empty_list():
    assert embed_texts([]) == []


def test_similar_texts_are_closer_than_dissimilar_ones():
    import numpy as np

    vectors = embed_texts(
        ["The cat sat on the mat.", "A cat is sitting on a mat.", "Stock markets fell sharply today."]
    )
    a, b, c = (np.array(v) for v in vectors)

    def cosine(x, y):
        return x @ y / (np.linalg.norm(x) * np.linalg.norm(y))

    assert cosine(a, b) > cosine(a, c)
