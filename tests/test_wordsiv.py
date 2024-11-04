import wordsiv
import pytest
from wordsiv import WordSiv, FilterError, Vocab
import string


@pytest.fixture(scope="session")
def wsv():
    test_data = "apple\t3\nbanana\t2\ncat\t1"
    w = WordSiv(add_default_vocabs=False)
    vocab = Vocab(bicameral=True, lang="en", data=test_data)
    w.add_vocab("test", vocab)
    w.set_vocab("test")
    return w


def test_paragraph_no_punctuation(wsv):
    assert not any(punct in wsv.para(glyphs="Ccat") for punct in string.punctuation)


def test_sentence_cap_first_default_true(wsv):
    # do cap_first by default if we have a capital
    assert wsv.sent(glyphs="Apple")[0].isupper()

    # if we don't have any capitals, cap_first should be false
    assert wsv.sent(glyphs="apple")[0].islower()

    # if we ask for a capitalized sentence and we don't have any capitals, we'll just be missing the first word
    assert wsv.sent(glyphs="apple", cap_first=True, n_words=3) == "apple apple"

    # but if we set raise_errors=True, we should get an error
    with pytest.raises(FilterError):
        wsv.sent(glyphs="apple", cap_first=True, raise_errors=True)


@pytest.mark.parametrize("n_words", [1, 2, 10, 20])
def test_words_n_words(wsv, n_words):
    assert len(wsv.words(n_words=n_words)) == n_words


@pytest.mark.parametrize("n_words", [1, 2, 10, 20])
def test_num_words(wsv, n_words):
    assert len(wsv.sent(n_words=n_words).split(" ")) == n_words


@pytest.mark.parametrize("min_n_words, max_n_words", [(1, 1), (1, 2), (1, 10), (1, 20)])
def test_sentence_min_n_words_max_n_words(wsv, min_n_words, max_n_words):
    for _ in range(5):
        assert (
            min_n_words
            <= len(
                wsv.sent(min_n_words=min_n_words, max_n_words=max_n_words).split(" ")
            )
            <= max_n_words
        )


@pytest.mark.parametrize("n_sents", [1, 2, 10, 20])
def test_sentences_n_sents(wsv, n_sents):
    assert len(wsv.sents(n_sents=n_sents)) == n_sents


@pytest.mark.parametrize("min_n_sents, max_n_sents", [(1, 1), (1, 2), (1, 10), (1, 20)])
def test_sentences_min_n_sents_max_n_sents(wsv, min_n_sents, max_n_sents):
    for _ in range(5):
        assert (
            min_n_sents
            <= len(wsv.sents(min_n_sents=min_n_sents, max_n_sents=max_n_sents))
            <= max_n_sents
        )
