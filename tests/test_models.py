import wordsiv
import pytest
from wordsiv.sources import WordCountSource
from wordsiv.models import WordProbModel, FilterError
import string


@pytest.fixture(scope="session")
def wsv_probdist():
    test_punct = {
        "start": {"": 100},
        # make no ending punctuation extremely low probability so
        # it only happens when period is not available
        "end": {"": 0.00001, ".": 100, "?": 40, "!": 20},
        "inner": {"": 100, ",": 80, "-": 40, ":": 30, ";": 20},
        "wrap": {("", ""): 100, ("“", "”"): 9, ("‘", "’"): 6},
    }
    test_data = "apple\t3\nbanana\t2\ncat\t1"
    w = wordsiv.WordSiv()
    wc_source = WordCountSource(
        "fake/path", meta={"bicameral": "True"}, test_data=test_data
    )
    w.add_model("test", WordProbModel(wc_source, test_punct))
    w.set_model("test")
    return w


def test_probdist_paragraph_no_punctuation(wsv_probdist):
    assert not any(
        punct in wsv_probdist.para(glyphs="Ccat") for punct in string.punctuation
    )


def test_probdist_sentence_cap_first_default_true(wsv_probdist):
    # do cap_first by default if we have a capital
    assert wsv_probdist.sent(glyphs="Apple")[0].isupper()

    # if we don't have any capitals, cap_first should be false
    assert wsv_probdist.sent(glyphs="apple")[0].islower()

    # if we ask for a capitalized sentence and we don't have any capitals, we'll just be missing the first word
    assert (
        wsv_probdist.sent(glyphs="apple", cap_first=True, num_words=3) == "apple apple"
    )

    # but if we set raise_errors=True, we should get an error
    with pytest.raises(FilterError):
        wsv_probdist.sent(glyphs="apple", cap_first=True, raise_errors=True)


@pytest.mark.parametrize("num_words", [1, 2, 10, 20])
def test_probdist_words_num_words(wsv_probdist, num_words):
    assert len(wsv_probdist.words(num_words=num_words)) == num_words


@pytest.mark.parametrize("num_words", [1, 2, 10, 20])
def test_probdist_sentence_len(wsv_probdist, num_words):
    assert len(wsv_probdist.sent(num_words=num_words).split(" ")) == num_words


@pytest.mark.parametrize(
    "min_num_words, max_num_words", [(1, 1), (1, 2), (1, 10), (1, 20)]
)
def test_probdist_sentence_min_num_words_max_num_words(
    wsv_probdist, min_num_words, max_num_words
):
    for _ in range(5):
        assert (
            min_num_words
            <= len(
                wsv_probdist.sent(
                    min_num_words=min_num_words, max_num_words=max_num_words
                ).split(" ")
            )
            <= max_num_words
        )


@pytest.mark.parametrize("para_len", [1, 2, 10, 20])
def test_probdist_sentences_para_len(wsv_probdist, para_len):
    assert len(wsv_probdist.sents(para_len=para_len)) == para_len


@pytest.mark.parametrize(
    "min_para_len, max_para_len", [(1, 1), (1, 2), (1, 10), (1, 20)]
)
def test_probdist_sentences_min_para_len_max_para_len(
    wsv_probdist, min_para_len, max_para_len
):
    for _ in range(5):
        assert (
            min_para_len
            <= len(
                wsv_probdist.sents(min_para_len=min_para_len, max_para_len=max_para_len)
            )
            <= max_para_len
        )
