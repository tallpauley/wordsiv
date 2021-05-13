import wordsiv
from wordsiv.text_models.markov import MarkovSource
from pathlib import Path
from test_source_modules import mkvtest
import pytest

HERE = Path(__file__).parent.absolute()
LIMITED_CHARS = "HAMBURGERFONTSIVhamburgerfontsiv"


@pytest.fixture(scope="session")
def wsv_mk():
    w = wordsiv.WordSiv()
    w.add_source_module(mkvtest)
    return w


#####################################################################################
###### TEST LIMIT_GLYPHS
#####################################################################################


@pytest.fixture(scope="session")
def wsv_mk_limited():
    w = wordsiv.WordSiv(limit_glyphs=LIMITED_CHARS)
    w.add_source_module(mkvtest)
    return w


def test_limit_glyphs(wsv_mk_limited):
    assert all(
        [
            c in LIMITED_CHARS + " \n"
            for c in wsv_mk_limited.text(source="mkvtest", model="markov", num_paras=10)
        ]
    )


#####################################################################################
###### TEST WORD CASE
#####################################################################################


def capitalized(w):
    return (
        w[0].isupper() if len(w) == 1 else w[0].isupper() and "".join(w[1:]).islower()
    )


# not supported
def test_word(wsv_mk):
    with pytest.raises(NotImplementedError):
        wsv_mk.word(source="mkvtest", model="markov")


# not supported
def test_words(wsv_mk):
    with pytest.raises(NotImplementedError):
        wsv_mk.words(source="mkvtest", model="markov")


@pytest.mark.parametrize("wsv_func", ["sentence", "paragraph", "text"])
def test_lc_string(wsv_mk, wsv_func):
    assert getattr(wsv_mk, wsv_func)(source="mkvtest", model="markov", lc=True).islower()


@pytest.mark.parametrize("wsv_func", ["sentence", "paragraph", "text"])
def test_uc_string(wsv_mk, wsv_func):
    assert getattr(wsv_mk, wsv_func)(source="mkvtest", model="markov", uc=True).isupper()


# not supported
def test_cap_sent_sentence(wsv_mk):
    with pytest.raises(TypeError):
        sent = wsv_mk.sentence(source="mkvtest", model="markov", cap_sent=True)
