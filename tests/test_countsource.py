import wordsiv
from wordsiv.models.wordcount import WordCountSource
from pathlib import Path
import pytest

HERE = Path(__file__).parent.absolute()
LIMITED_CHARS = "HAMBURGERFONTSIVhamburgerfontsiv"


@pytest.fixture(scope="session")
def wsv_wc():
    w = wordsiv.WordSiv()
    w.sources["test"] = WordCountSource(HERE / "data" / "count-source.txt")
    return w


#####################################################################################
###### TEST LIMIT_GLYPHS
#####################################################################################


@pytest.fixture(scope="session")
def wsv_wc_limited():
    w = wordsiv.WordSiv(limit_glyphs=LIMITED_CHARS)
    w.sources["test"] = WordCountSource(HERE / "data" / "count-source.txt")
    return w


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_limit_glyphs(wsv_wc_limited, model):
    assert all([
        c in LIMITED_CHARS + ' \n'
        for c in wsv_wc_limited.text(source="test", model=model, num_paras=10)
    ])


#####################################################################################
###### TEST WORD CASE
#####################################################################################


def capitalized(w):
    return (
        w[0].isupper() if len(w) == 1 else w[0].isupper() and "".join(w[1:]).islower()
    )


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_lc_string(wsv_wc, model, wsv_func):
    assert getattr(wsv_wc, wsv_func)(source="test", model=model, lc=True).islower()


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_lc_list(wsv_wc, model, wsv_func):
    assert all(
        s.islower()
        for s in getattr(wsv_wc, wsv_func)(source="test", model=model, lc=True)
    )


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_uc_string(wsv_wc, model, wsv_func):
    assert getattr(wsv_wc, wsv_func)(source="test", model=model, uc=True).isupper()


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_uc_list(wsv_wc, model, wsv_func):
    assert all(
        [
            s.isupper()
            for s in getattr(wsv_wc, wsv_func)(source="test", model=model, uc=True)
        ]
    )


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_cap_word(wsv_wc, model):
    assert capitalized(wsv_wc.word(source="test", model=model, cap=True))


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
@pytest.mark.parametrize("wsv_func", ["words"])
def test_cap_list(wsv_wc, model, wsv_func):
    assert all(
        [
            capitalized(s)
            for s in getattr(wsv_wc, wsv_func)(source="test", model=model, cap=True)
        ]
    )


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_cap_first_words(wsv_wc, model):
    sent = wsv_wc.words(source="test", model=model, cap_first=True)
    # just check first word capitalized, we don't enforce any particular capitalization
    # on other words with this parameter
    assert capitalized(sent[0])


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_cap_sent_sentence(wsv_wc, model):
    sent = wsv_wc.sentence(source="test", model=model, cap_sent=True)
    assert sent[0].isupper() and sent[1].islower()


#####################################################################################
###### TEST OTHER FILTERS
#####################################################################################


@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_word_length(wsv_wc, model):
    assert len(wsv_wc.word(source="test", model=model, wl=4)) == 4


def gen_range_tuples(max):
    for n in range(1, max):
        for n2 in range(n, max):
            yield (n, n2)


@pytest.mark.parametrize("min_len,max_len", tuple(gen_range_tuples(20)))
@pytest.mark.parametrize("model", ["prob", "top", "rand"])
def test_word_length(wsv_wc, min_len, max_len, model):
    word = wsv_wc.word(source="test", model=model, min_wl=min_len, max_wl=max_len)
    assert len(word) >= min_len and len(word) <= max_len
