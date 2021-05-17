import wordsiv
from wordsiv.sentence_models_sources import MarkovSource
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
def wsv_limit_glyphs_mkv():
    w = wordsiv.WordSiv(limit_glyphs=LIMITED_CHARS)
    w.add_source_module(mkvtest)
    return w


@pytest.fixture(scope="session")
def wsv_font_file_mkv():
    w = wordsiv.WordSiv(font_file=HERE / "data/noto-sans-subset.ttf")
    w.add_source_module(mkvtest)
    return w


def test_limit_glyphs(wsv_limit_glyphs_mkv):

    unexpected_chars = " ".join(
        set(
            c
            for c in wsv_limit_glyphs_mkv.text(
                source="mkvtest", model="mkv", num_paras=10
            )
            if c not in LIMITED_CHARS + " \n"
        )
    )
    assert not unexpected_chars


def test_font_file(wsv_font_file_mkv):

    unexpected_chars = " ".join(
        set(
            c
            for c in wsv_font_file_mkv.text(source="mkvtest", model="mkv", num_paras=10)
            if c not in LIMITED_CHARS + " \n"
        )
    )
    assert not unexpected_chars


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
        wsv_mk.word(source="mkvtest", model="mkv")


# not supported
def test_words(wsv_mk):
    with pytest.raises(NotImplementedError):
        wsv_mk.words(source="mkvtest", model="mkv")


@pytest.mark.parametrize("wsv_func", ["sentence", "paragraph", "text"])
def test_lc_string(wsv_mk, wsv_func):
    assert getattr(wsv_mk, wsv_func)(source="mkvtest", model="mkv", lc=True).islower()


@pytest.mark.parametrize("wsv_func", ["sentence", "paragraph", "text"])
def test_uc_string(wsv_mk, wsv_func):
    assert getattr(wsv_mk, wsv_func)(source="mkvtest", model="mkv", uc=True).isupper()


# not supported
def test_cap_sent_sentence(wsv_mk):
    with pytest.raises(TypeError):
        sent = wsv_mk.sentence(source="mkvtest", model="mkv", cap_sent=True)


#####################################################################################
###### TEST SENTENCE LENGTH
#####################################################################################


@pytest.mark.parametrize("min_sl,max_sl", [(3, 7)])
def test_sentence_length(wsv_mk, min_sl, max_sl):
    sentence = wsv_mk.sentence(
        source="mkvtest",
        model="mkv",
        min_sent_len=min_sl,
        max_sent_len=max_sl,
    )
    sentence_len = len(sentence.split(" "))

    assert min_sl < sentence_len < max_sl
