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
        punct in wsv_probdist.paragraph(glyphs="Ccat") for punct in string.punctuation
    )


def test_probdist_sentence_cap_sent_default_true(wsv_probdist):
    # do cap_sent by default if we have a capital
    assert wsv_probdist.sentence(glyphs="Apple")[0].isupper()

    # if we don't have any capitals, cap_sent should be false
    assert wsv_probdist.sentence(glyphs="apple")[0].islower()

    # if we are asking for cap_sent, and we don't have capitals, throw an error...
    with pytest.raises(FilterError):
        wsv_probdist.sentence(glyphs="apple", cap_sent=True)


@pytest.mark.parametrize("num_words", [1, 2, 10, 20])
def test_probdist_words_num_words(wsv_probdist, num_words):
    assert len(wsv_probdist.words(num_words=num_words)) == num_words


@pytest.mark.parametrize("sent_len", [1, 2, 10, 20])
def test_probdist_sentence_len(wsv_probdist, sent_len):
    assert len(wsv_probdist.sentence(sent_len=sent_len).split(" ")) == sent_len


@pytest.mark.parametrize(
    "min_sent_len, max_sent_len", [(1, 1), (1, 2), (1, 10), (1, 20)]
)
def test_probdist_sentence_min_sent_len_max_sent_len(
    wsv_probdist, min_sent_len, max_sent_len
):
    for _ in range(5):
        assert (
            min_sent_len
            <= len(
                wsv_probdist.sentence(
                    min_sent_len=min_sent_len, max_sent_len=max_sent_len
                ).split(" ")
            )
            <= max_sent_len
        )


@pytest.mark.parametrize("para_len", [1, 2, 10, 20])
def test_probdist_sentences_para_len(wsv_probdist, para_len):
    assert len(wsv_probdist.sentences(para_len=para_len)) == para_len


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
                wsv_probdist.sentences(
                    min_para_len=min_para_len, max_para_len=max_para_len
                )
            )
            <= max_para_len
        )
