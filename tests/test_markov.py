import wordsiv
from wordsiv.models.markov import MarkovSource
from pathlib import Path
import pytest

HERE = Path(__file__).parent.absolute()

wsv = wordsiv.WordSiv(limit_glyphs="HAMBURGERFONTSIVhamburgerfontsiv")
wsv.sources["test"] = MarkovSource(HERE / "data" / "markov-source.json")


def capitalized(w):
    return w[0].isupper() and w[1:].islower()


def test_word():
    with pytest.raises(NotImplementedError):
        wsv.word(source="test", model="markov")


def test_words():
    with pytest.raises(NotImplementedError):
        wsv.words(source="test", model="markov")


@pytest.mark.parametrize("wsv_func", ["sentence", "paragraph", "text"])
def test_lc_string(wsv_func):
    assert getattr(wsv, wsv_func)(source="test", model="markov", lc=True).islower()


@pytest.mark.parametrize("wsv_func", ["sentence", "paragraph", "text"])
def test_uc_string(wsv_func):
    assert getattr(wsv, wsv_func)(source="test", model="markov", uc=True).isupper()


def test_cap_sent_sentence():
    sent = wsv.sentence(source="test", model="markov", cap_sent=True)
    assert sent[0].isupper()
