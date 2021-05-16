import wordsiv
from wordsiv.sentence_models_sources import WordCountSource
from pathlib import Path
from test_source_modules import wctest
import pytest

HERE = Path(__file__).parent.absolute()
LIMITED_CHARS = "HAMBURGERFONTSIVhamburgerfontsiv"


@pytest.fixture(scope="session")
def wsv_wc():
    w = wordsiv.WordSiv()
    w.add_source_module(wctest)
    return w


#####################################################################################
###### TEST LIMIT_GLYPHS
#####################################################################################


@pytest.fixture(scope="session")
def wsv_limit_glyphs_wc():
    w = wordsiv.WordSiv(limit_glyphs=LIMITED_CHARS)
    w.add_source_module(wctest)
    return w


def test_limit_glyphs(wsv_limit_glyphs_wc):
    assert all(
        [
            c in LIMITED_CHARS + " \n"
            for c in wsv_limit_glyphs_wc.text(
                source="wctest", model="rand", num_paras=10
            )
        ]
    )


#####################################################################################
###### TEST FONT FILE
#####################################################################################


@pytest.fixture(scope="session")
def wsv_font_file_wc():
    w = wordsiv.WordSiv(font_file=HERE / "data/noto-sans-subset.ttf")
    w.add_source_module(wctest)
    return w


def test_font_file(wsv_font_file_wc):
    assert all(
        [
            c in LIMITED_CHARS + " \n"
            for c in wsv_font_file_wc.text(source="wctest", model="rand", num_paras=10)
        ]
    )


def test_width(wsv_font_file_wc):
    assert (
        wsv_font_file_wc.word(source="wctest", model="rand", width=15622)
        == "instrumentation"
    )


@pytest.mark.parametrize("model", ["seq", "rand"])
def test_width_range(wsv_font_file_wc, model):
    # TODO I think whatever the width filter does is NOT deterministic
    assert wsv_font_file_wc.words(
        num_words=5, source="wctest", model=model, min_width=1000, max_width=5000
    )[4]


#####################################################################################
###### TEST WORD CASE
#####################################################################################


def capitalized(w):
    return (
        w[0].isupper() if len(w) == 1 else w[0].isupper() and "".join(w[1:]).islower()
    )


@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_lc_string(wsv_wc, wsv_func):
    assert getattr(wsv_wc, wsv_func)(source="wctest", model="rand", lc=True).islower()


@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_lc_list(wsv_wc, wsv_func):
    assert all(
        s.islower()
        for s in getattr(wsv_wc, wsv_func)(source="wctest", model="rand", lc=True)
    )


@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_uc_string(wsv_wc, wsv_func):
    assert getattr(wsv_wc, wsv_func)(source="wctest", model="rand", uc=True).isupper()


@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_uc_list(wsv_wc, wsv_func):
    assert all(
        [
            s.isupper()
            for s in getattr(wsv_wc, wsv_func)(source="wctest", model="rand", uc=True)
        ]
    )


@pytest.mark.parametrize("model", ["seq", "rand"])
def test_cap_word(wsv_wc, model):
    assert all(
        [capitalized(w) for w in wsv_wc.words(source="wctest", model=model, cap=True)]
    )


def test_cap_first_words(wsv_wc):
    sent = wsv_wc.words(source="wctest", model="rand", cap_first=True)
    # just check first word capitalized, we don't enforce any particular capitalization
    # on other words with this parameter
    assert capitalized(sent[0])


def test_cap_sent_sentence(wsv_wc):
    sent = wsv_wc.sentence(source="wctest", model="rand", cap_sent=True)
    assert sent[0].isupper() and sent[1].islower()


#####################################################################################
###### TEST OTHER FILTERS
#####################################################################################


@pytest.mark.rangetest
@pytest.mark.parametrize("wl", range(1, 20))
@pytest.mark.parametrize("model", ["seq", "rand"])
def test_word_length(wsv_wc, model, wl):
    assert all(
        [len(w) == wl for w in wsv_wc.words(source="wctest", model=model, wl=wl)]
    )


def gen_range_tuples(max):
    for n in range(1, max):
        for n2 in range(n, max):
            yield (n, n2)


@pytest.mark.rangetest
@pytest.mark.parametrize("min_len,max_len", tuple(gen_range_tuples(20)))
def test_word_length(wsv_wc, min_len, max_len):
    word = wsv_wc.word(source="wctest", model="rand", min_wl=min_len, max_wl=max_len)
    assert len(word) >= min_len and len(word) <= max_len


#####################################################################################
###### TEST
#####################################################################################
