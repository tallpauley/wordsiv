import wordsiv
from wordsiv.models.wordcount import WordCountSource
from pathlib import Path
import pytest

HERE = Path(__file__).parent.absolute()

wsv = wordsiv.WordSiv(limit_glyphs="HAMBURGERFONTSIVhamburgerfontsiv")
wsv.sources["test"] = WordCountSource(HERE / "data" / "count-source.txt")

#####################################################################################
###### TEST WORD CASE
#####################################################################################


def capitalized(w):
    return (
        w[0].isupper() if len(w) == 1 else w[0].isupper() and "".join(w[1:]).islower()
    )


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_lc_string(model, wsv_func):
    assert getattr(wsv, wsv_func)(source="test", model=model, lc=True).islower()


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_lc_list(model, wsv_func):
    assert all(
        s.islower() for s in getattr(wsv, wsv_func)(source="test", model=model, lc=True)
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
    # just check first word capitalized, we don't enforce any particular capitalization
    # on other words with this parameter
    assert capitalized(sent[0])


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_cap_sent_sentence(model):
    sent = wsv.sentence(source="test", model=model, cap_sent=True)
    assert sent[0].isupper() and sent[1].islower()


#####################################################################################
###### TEST OTHER FILTERS
#####################################################################################


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_word_length(model):
    assert len(wsv.word(source="test", model=model, wl=4)) == 4


# @pytest.mark.parametrize("min, max", )
# @pytest.mark.parametrize("model", ["prob", "top", "rand"])
# def test_word_length(min_len, max_len, model):
#     try:
#         word = wsv.word(source="test", model=model, min_wl=min_len, max_wl=max_len)
#         assert len(word) >= min_len and len(word) <= max_len
#     except ValueError:
#          pytest.skip("No words in this range")
