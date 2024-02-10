import wordsiv
from wordsiv.sentence_models_sources import WordCountSource
from pathlib import Path
from test_source_modules import wctest
import pytest
from collections import Counter
import re

HERE = Path(__file__).parent.absolute()
LIMITED_CHARS = "HAMBURGERFONTSIVhamburgerfontsiv"
LIMITED_PUNCT = ".,:;”“"


@pytest.fixture(scope="session")
def wsv_wc():
    w = wordsiv.WordSiv()
    w.add_source_module(wctest)
    return w


#####################################################################################
###### TEST glyphs
#####################################################################################


@pytest.fixture(scope="session")
def wsv_limit_glyphs_wc():
    w = wordsiv.WordSiv(glyphs=LIMITED_CHARS)
    w.add_source_module(wctest)
    return w


def test_limit_glyphs(wsv_limit_glyphs_wc):
    unexpected_chars = " ".join(
        set(
            c
            for c in wsv_limit_glyphs_wc.text(
                source="wctest", model="rand", num_paras=10
            )
            if c not in LIMITED_CHARS + " \n"
        )
    )
    assert not unexpected_chars


#####################################################################################
###### TEST NUM_WORDS AND SENTENCE/PARAGRAPH LENGTHS
#####################################################################################


@pytest.mark.parametrize("num", [1, 10, 20])
def test_num_words(wsv_wc, num):
    assert len(wsv_wc.words(source="wctest", num_words=num)) == num


@pytest.mark.parametrize("num", [3, 10, 20])
def test_num_words(wsv_wc, num):
    assert len(wsv_wc.sentence(source="wctest", sent_len=num).split(" ")) == num


@pytest.mark.parametrize("range", ((1, 10), (5, 9)))
def test_num_words_range(wsv_wc, range):
    assert (
        range[0]
        <= len(
            wsv_wc.sentence(
                source="wctest", min_sent_len=range[0], max_sent_len=range[1]
            ).split(" ")
        )
        <= range[1]
    )


@pytest.mark.parametrize("num", [1, 3, 15])
def test_para_len(wsv_wc, num):
    def mock_punc_func(words, rand, start, end, inner, wrap):
        return " ".join(words) + "."

    assert (
        len(
            wsv_wc.paragraph(
                source="wctest", sent_len=3, punc_func=mock_punc_func, para_len=num
            ).split(".")[:-1]
        )
        == num
    )


@pytest.mark.parametrize("num", [1, 3, 15])
def test_num_paras(wsv_wc, num):
    assert len(wsv_wc.text(source="wctest", num_paras=num).split("\n\n")) == num


@pytest.mark.parametrize("w,h", [(1, 1), (3, 2), (6, 9)])
def test_block_para(wsv_wc, w, h):
    para = wsv_wc.paragraph(
        source="wctest", model="seq", para_len=h, sent_len=w, sent_sep="\n"
    )
    num_lines = para.count("\n") + 1
    first_line = para.split("\n")[0]
    assert num_lines == h and len(first_line.split(" ")) == w


#####################################################################################
###### TEST MODEL BEHAVIORS
#####################################################################################


def test_sequential(wsv_wc):
    assert wsv_wc.words(source="wctest", model="seq", num_words=7) == [
        "gather",
        "to",
        "sublimedirectory",
        "sublimedirectory",
        "consultation",
        "other",
        "componentartscstamp",
    ]


def test_sequential_loops(wsv_wc):
    assert len(wsv_wc.words(source="wctest", model="seq", num_words=100)) == 100


#####################################################################################
###### TEST PUNCTUATION
#####################################################################################


@pytest.fixture(scope="session")
def wsv_limit_glyphs_wc_punc():
    w = wordsiv.WordSiv(glyphs=LIMITED_CHARS + LIMITED_PUNCT)
    w.add_source_module(wctest)
    return w


def test_default_punc_func(wsv_limit_glyphs_wc_punc):
    text = wsv_limit_glyphs_wc_punc.text(source="wctest", num_paras=100)
    assert all(c in text for c in LIMITED_PUNCT)


def test_default_punc_freq(wsv_limit_glyphs_wc_punc):
    text = wsv_limit_glyphs_wc_punc.text(source="wctest", num_paras=100)
    text_len = len(text)
    counts = dict(
        {c: count for c, count in Counter(text).items() if c in LIMITED_PUNCT}
    )
    punc_count = sum(counts.values())
    punc_percents = {c: (float(count) / punc_count) for c, count in counts.items()}
    assert (0.4 < punc_percents["."] < 0.6) and (0.1 < punc_percents[","] < 0.3)


#####################################################################################
###### TEST WORD CASE
#####################################################################################


def capitalized(w):
    return (
        w[0].isupper() if len(w) == 1 else w[0].isupper() and "".join(w[1:]).islower()
    )


@pytest.mark.parametrize("prob", [True, False])
@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_lc_string(wsv_wc, wsv_func, prob):
    assert getattr(wsv_wc, wsv_func)(
        prob=prob, source="wctest", model="rand", lc=True
    ).islower()


@pytest.mark.parametrize("prob", [True, False])
@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_lc_list(wsv_wc, wsv_func, prob):
    assert all(
        s.islower()
        for s in getattr(wsv_wc, wsv_func)(
            prob=prob, source="wctest", model="rand", lc=True
        )
    )


@pytest.mark.parametrize("prob", [True, False])
@pytest.mark.parametrize("wsv_func", ["word", "sentence", "paragraph", "text"])
def test_uc_string(wsv_wc, wsv_func, prob):
    assert getattr(wsv_wc, wsv_func)(source="wctest", model="rand", uc=True).isupper()


@pytest.mark.parametrize("prob", [True, False])
@pytest.mark.parametrize("wsv_func", ["words", "sentences", "paragraphs"])
def test_uc_list(wsv_wc, wsv_func, prob):
    assert all(
        [
            s.isupper()
            for s in getattr(wsv_wc, wsv_func)(
                prob=prob, source="wctest", model="rand", uc=True
            )
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
    sent_no_punc = re.sub(r"[^\w\s]", "", sent)
    assert sent_no_punc[0].isupper() and not (sent_no_punc[1:].isupper())


#####################################################################################
###### TEST OTHER FILTERS
#####################################################################################


@pytest.mark.parametrize("model", ["seq", "rand"])
def test_no_words(wsv_wc, model):
    with pytest.raises(ValueError):
        wsv_wc.words(source="wctest", model=model, min_wl=1000)


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
