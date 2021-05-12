import wordsiv
from wordsiv.models.wordcount import WordCountSource
from pathlib import Path
import pytest

HERE = Path(__file__).parent.absolute()

wsv = wordsiv.WordSiv(limit_glyphs="HAMBURGERFONTSIVhamburgerfontsiv")
wsv.sources["test"] = WordCountSource(HERE / "data" / "count-source.txt")


def capitalized(w):
    return w[0].isupper() and w[1:].islower()


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_lc_string(model, wsv_func):
    assert getattr(wsv, wsv_func)(source="test", model=model, lc=True).islower()


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_lc_list(model, wsv_func):
    assert all(
        s.islower()
        for s in getattr(wsv, wsv_func)(source="test", model=model, lc=True)
    )


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_uc_string(model, wsv_func):
    assert getattr(wsv, wsv_func)(source="test", model=model, uc=True).isupper()


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_uc_list(model, wsv_func):
    assert all(
        [
            s.isupper()
            for s in getattr(wsv, wsv_func)(source="test", model=model, uc=True)
        ]
    )


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_cap_word(model):
    assert capitalized(wsv.word(source="test", model=model, cap=True))


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["words"])
def test_cap_list(model, wsv_func):
    assert all(
        [
            capitalized(s)
            for s in getattr(wsv, wsv_func)(source="test", model=model, cap=True)
        ]
    )


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_cap_first_words(model):
    sent = wsv.words(source="test", model=model, cap_first=True)
    assert capitalized(sent[0]) and all(w.islower() for w in sent[1:])


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_cap_sent_sentence(model):
    sent = wsv.sentence(source="test", model=model, cap_sent=True)
    assert sent[0].isupper() and sent[1].islower()
