import pytest
from wordsiv import WordSiv, FilterError, Vocab
import string
import re


@pytest.fixture(scope="session")
def wsv():
    test_data = "apple\t3\nbanana\t2\ncat\t1"
    w = WordSiv(add_default_vocabs=False)
    vocab = Vocab(bicameral=True, lang="en", data=test_data)
    w.add_vocab("test", vocab)
    w.vocab = "test"
    return w


def test_wordsiv_no_default_punctuation_for_vocab_ignores_punctuation():
    w = WordSiv(add_default_vocabs=False)
    test_data = "apple\t3\nbanana\t2\ncat\t1"
    vocab = Vocab(bicameral=True, lang="xx", data=test_data)
    w.add_vocab("test", vocab)
    w.vocab = "test"
    assert len(w.sent()) > 1


def test_wordsiv_vocab_with_custom_punctuation():
    w = WordSiv(add_default_vocabs=True)
    punc_dict = {
        "insert": {
            "–": 1,
        },
        "wrap_sent": {
            ("?", "!"): 1,
        },
        "wrap_inner": {
            ("(", ")"): 1,
        },
    }
    test_data = "apple\t3\nbanana\t2\ncat\t1"
    w = WordSiv(add_default_vocabs=False)
    vocab = Vocab(bicameral=True, lang="en", data=test_data, punctuation=punc_dict)
    w.add_vocab("test", vocab)
    w.vocab = "test"
    sentence = w.sent()
    assert all(punc in sentence for punc in "–()")
    assert sentence.startswith("?")
    assert sentence.endswith("!")


def test_wordsiv_add_list_default_vocabs():
    w = WordSiv(add_default_vocabs=True)
    vocabs = w.list_vocabs()
    assert all(isinstance(v, str) for v in vocabs)
    assert len(vocabs) > 1


@pytest.mark.parametrize("min_wl, max_wl", [(1, 1), (1, 2), (1, 4)])
def test_number_min_max_wl(wsv, min_wl, max_wl):
    number = wsv.number(min_wl=min_wl, max_wl=max_wl)
    assert min_wl <= len(number) <= max_wl


def test_number_min_max_wl_throws_valueerror(wsv):
    with pytest.raises(ValueError):
        wsv.number(min_wl=5, max_wl=1)


def test_number_glyphs_no_numerals_throws_filtererror(wsv):
    with pytest.raises(FilterError):
        wsv.number(glyphs="abc", raise_errors=True)


def test_number_glyphs_no_numerals(wsv):
    assert wsv.number(glyphs="abc") == ""


@pytest.mark.parametrize("wl", [1, 2, 4])
def test_number_wl(wsv, wl):
    number = wsv.number(wl=wl)
    assert len(number) == wl


def test_number_with_seed(wsv):
    seed = 12345
    number1 = wsv.number(seed=seed)
    number2 = wsv.number(seed=seed)
    assert number1 == number2


def test_number_glyphs(wsv):
    glyphs = "123"
    number = wsv.number(glyphs=glyphs, min_wl=1, max_wl=4)
    assert all(char in glyphs for char in number)


def test_number_no_glyphs_raises_error(wsv):
    with pytest.raises(FilterError):
        wsv.number(glyphs="abc", raise_errors=True)


def test_top_word_idx_unavailable_returns_empty_string(wsv):
    assert wsv.top_word(idx=4) == ""


def test_top_word_no_results_returns_empty_string(wsv):
    assert wsv.top_word(contains="xyz") == ""


def test_top_word_no_results_throws_filtererror(wsv):
    with pytest.raises(FilterError):
        wsv.top_word(contains="xyz", raise_errors=True)


def test_top_word_idx_unavailable_throws_filtererror(wsv):
    with pytest.raises(FilterError):
        wsv.top_word(idx=4, raise_errors=True)


def test_top_words(wsv):
    assert wsv.top_words() == ["apple", "banana", "cat"]


def test_top_words_idx_unavailable_returns_empty_string(wsv):
    assert wsv.top_words(idx=4) == []


def test_top_words_idx_unavailable_throws_filtererror(wsv):
    with pytest.raises(FilterError):
        wsv.top_words(idx=4, raise_errors=True)


def test_top_words_no_results_throws_filtererror(wsv):
    with pytest.raises(FilterError):
        wsv.top_words(contains="xyz", raise_errors=True)


def test_top_words_no_results_returns_empty_list(wsv):
    assert wsv.top_words(contains="xyz") == []


def test_word_rnd_out_of_range_raises_valueerror(wsv):
    with pytest.raises(ValueError):
        wsv.word(rnd=1.1)


def test_words_top_k(wsv):
    assert "cat" not in wsv.words(top_k=2, n_words=100)


def test_words_numbers_out_of_range_raises_valueerror(wsv):
    with pytest.raises(ValueError):
        wsv.words(numbers=1.1)


def test_sent_rnd_punc_out_of_range_raises_valueerror(wsv):
    with pytest.raises(ValueError):
        wsv.sent(rnd_punc=1.1)


def test_sent_missing_vocab_raises_keyerror(wsv):
    with pytest.raises(KeyError):
        wsv.sent(vocab="fake")


def test_sent_undefined_vocab_raises_valueerror():
    test_data = "apple\t3\nbanana\t2\ncat\t1"
    w = WordSiv(add_default_vocabs=False)
    vocab = Vocab(bicameral=True, lang="en", data=test_data)
    w.add_vocab("test", vocab)
    with pytest.raises(ValueError):
        w.sent()


def test_paragraph_no_punctuation(wsv):
    assert not any(punct in wsv.para(glyphs="Ccat") for punct in string.punctuation)


def test_sentence_cap_first_default_true(wsv):
    # do cap_first by default if we have a capital
    assert wsv.sent(glyphs="Apple")[0].isupper()

    # if we don't have any capitals, cap_first should be false
    assert wsv.sent(glyphs="apple")[0].islower()

    # if we ask for a capitalized sentence and we don't have any capitals, we'll just be missing the first word
    assert wsv.sent(glyphs="apple", cap_first=True, n_words=3) == "apple apple"

    # but if we set raise_errors=True, we should get an error
    with pytest.raises(FilterError):
        wsv.sent(glyphs="apple", cap_first=True, raise_errors=True)


@pytest.mark.parametrize("n_words", [1, 2, 10, 20])
def test_words_n_words(wsv, n_words):
    assert len(wsv.words(n_words=n_words)) == n_words


@pytest.mark.parametrize("n_words", [1, 2, 10, 20])
def test_sent_n_words_no_punc(wsv, n_words):
    assert len(wsv.sent(n_words=n_words, punc=False).split(" ")) == n_words


@pytest.mark.parametrize("min_n_words, max_n_words", [(1, 1), (1, 2), (1, 10), (1, 20)])
def test_sentence_min_n_words_max_n_words(wsv, min_n_words, max_n_words):
    for _ in range(5):
        assert (
            min_n_words
            <= len(
                wsv.sent(
                    min_n_words=min_n_words, max_n_words=max_n_words, punc=False
                ).split(" ")
            )
            <= max_n_words
        )


def test_wordsiv_seed(wsv):
    wsv.seed(1)
    assert wsv.word() == "apple"
    wsv.seed(1)
    assert wsv.word() == "apple"


@pytest.mark.parametrize(
    "function",
    ["word", "number", "words", "sent", "sents", "para", "paras", "text"],
)
@pytest.mark.parametrize("seed", [35, "HAMBURG", 12.5])
def test_seed_reproduces_same_output(wsv, function, seed):
    f = getattr(wsv, function)
    assert f(seed=seed) == f(seed=seed)


@pytest.mark.parametrize("n_sents", [1, 2, 10, 20])
def test_sentences_n_sents(wsv, n_sents):
    assert len(wsv.sents(n_sents=n_sents)) == n_sents


@pytest.mark.parametrize("min_n_sents, max_n_sents", [(1, 1), (1, 2), (1, 10), (1, 20)])
def test_sentences_min_n_sents_max_n_sents(wsv, min_n_sents, max_n_sents):
    for _ in range(5):
        assert (
            min_n_sents
            <= len(wsv.sents(min_n_sents=min_n_sents, max_n_sents=max_n_sents))
            <= max_n_sents
        )


def test_all_numbers_arg_equals_1_returns_only_digits(wsv):
    glyphs = "hambuger0123"
    results = (
        " ".join(wsv.words(glyphs=glyphs, numbers=1))
        + wsv.sent(glyphs=glyphs, numbers=1, punc=False)
        + " ".join(wsv.sents(glyphs=glyphs, numbers=1, punc=False))
        + wsv.para(glyphs=glyphs, numbers=1, punc=False)
        + " ".join(wsv.paras(glyphs=glyphs, numbers=1, punc=False))
        + wsv.text(glyphs=glyphs, numbers=1, punc=False)
    )
    results_no_whitespace = re.sub(r"\s+", "", results)
    assert all(char.isdigit() for char in results_no_whitespace)


def test_all_numbers_arg_equals_0_returns_no_digits(wsv):
    glyphs = "hambuger0123"
    results = (
        " ".join(wsv.words(glyphs=glyphs, numbers=0))
        + wsv.sent(glyphs=glyphs, numbers=0, punc=False)
        + " ".join(wsv.sents(glyphs=glyphs, numbers=0, punc=False))
        + wsv.para(glyphs=glyphs, numbers=0, punc=False)
        + " ".join(wsv.paras(glyphs=glyphs, numbers=0, punc=False))
        + wsv.text(glyphs=glyphs, numbers=0, punc=False)
    )
    results_no_whitespace = re.sub(r"\s+", "", results)
    assert not any(char.isdigit() for char in results_no_whitespace)
