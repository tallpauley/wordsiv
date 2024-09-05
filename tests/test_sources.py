from wordsiv.sources import WordCountSource
import pytest

import pytest
from wordsiv.sources import FilterError, SourceEmptyError, SourceFormatError


def test_wordcountsource_no_data():
    test_data = ""
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(SourceEmptyError):
        wc.filter_data(None)


def test_wordcountsource_bad_format():
    test_data = "123\t123"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(SourceFormatError):
        wc.filter_data(None)


def test_wordcountsource_no_counts():
    test_data = "apple\nbanana\ncherry"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    assert wc.filter_data(None) == (("apple", 1), ("banana", 1), ("cherry", 1))


def test_filter_data_empty_glyphs():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(FilterError):
        wc.filter_data("xyz")


def test_filter_data_empty_word_length():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(FilterError):
        wc.filter_data(None, min_wl=10)


def test_filter_data_empty_contains():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(FilterError):
        wc.filter_data(None, contains="xyz")


def test_filter_data_empty_startswith():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(FilterError):
        wc.filter_data(None, startswith="x")


def test_filter_data_empty_endswith():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(FilterError):
        wc.filter_data(None, endswith="x")


def test_filter_data_empty_regexp():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(FilterError):
        wc.filter_data(None, regexp="x+")


def test_filter_data_glyphs():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    # if we have the letters to spell the word exactly as it is in the source, we'll match it
    assert wc.filter_data("aple") == (("apple", 2),)
    assert wc.filter_data("BARTDoS") == (("BART", 5), ("DDoS", 6))

    # if no exact matches for the glyph set, we'll match Cap and UC of lc source words
    assert wc.filter_data("GRAPEgrape") == (("grape", 1),)
    assert wc.filter_data("Grape") == (("Grape", 1),)
    assert wc.filter_data("GRAPE") == (("GRAPE", 1),)
    assert wc.filter_data("APLE") == (("APPLE", 2), ("APPLE", 3))

    # Capitalized, UC, CamelCaps words will not be lowercased,
    # since lowercasing an acronym or proper noun is often incorrect, however...
    with pytest.raises(FilterError):
        wc.filter_data("bartdos")


def test_filter_data_case():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    # if you do a fake case it'll throw a ValueError
    with pytest.raises(ValueError):
        wc.filter_data(None, case="fake")

    # with case='lc' and glyph = None, we'll just match words that are already lowercase
    assert wc.filter_data(None, case="lc") == (("grape", 1), ("apple", 2))

    # unless, you want to force them lowercase
    assert wc.filter_data(None, case="lc_force") == (
        ("grape", 1),
        ("apple", 2),
        ("apple", 3),
        ("bart", 4),
        ("bart", 5),
        ("ddos", 6),
    )

    # with case='uc', it assumes any word can be uppercased
    assert wc.filter_data(None, case="uc") == (
        ("GRAPE", 1),
        ("APPLE", 2),
        ("APPLE", 3),
        ("BART", 4),
        ("BART", 5),
        ("DDOS", 6),
    )

    # with case='cap', by default it only matches lowercase and capitalized words in the source
    assert wc.filter_data(None, case="cap") == (
        ("Grape", 1),
        ("Apple", 2),
        ("Apple", 3),
        ("Bart", 4),
    )

    # unless you want to force it with 'cap_force
    assert wc.filter_data(None, case="cap_force") == (
        ("Grape", 1),
        ("Apple", 2),
        ("Apple", 3),
        ("Bart", 4),
        ("Bart", 5),
        ("Ddos", 6),
    )


def test_filter_data_glyphs_case():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    # simple cases
    assert wc.filter_data(glyphs="aple", case="lc") == (("apple", 2),)
    assert wc.filter_data(glyphs="Aple", case="cap") == (("Apple", 2), ("Apple", 3))
    assert wc.filter_data(glyphs="APPLE", case="uc") == (("APPLE", 2), ("APPLE", 3))
    assert wc.filter_data(glyphs="BART", case="uc") == (("BART", 4), ("BART", 5))
    assert wc.filter_data(glyphs="DDOS", case="uc") == (("DDOS", 6),)

    # cases with no matches...
    with pytest.raises(FilterError):
        wc.filter_data(glyphs="bart", case="lc")

    with pytest.raises(FilterError):
        wc.filter_data(glyphs="Ddos", case="cap")

    # unless you want to force lc
    assert wc.filter_data(glyphs="bart", case="lc_force") == (
        ("bart", 4),
        ("bart", 5),
    )
    # or force cap
    assert wc.filter_data(glyphs="Ddos", case="cap_force") == (("Ddos", 6),)


def test_filter_data_wl():
    test_data = "apple\t10\nbanana\t5\njoe\t2"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    assert wc.filter_data(None, wl=3) == (("joe", 2),)
    assert wc.filter_data(None, min_wl=3) == (("apple", 10), ("banana", 5), ("joe", 2))
    assert wc.filter_data(None, min_wl=4) == (("apple", 10), ("banana", 5))
    assert wc.filter_data(None, min_wl=6) == (("banana", 5),)
    assert wc.filter_data(None, max_wl=3) == (("joe", 2),)


def test_filter_data_startswith_endswith_contains():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    assert wc.filter_data(None, startswith="a") == (("apple", 5),)
    assert wc.filter_data(None, contains="a") == (
        ("apple", 5),
        ("banana", 3),
        ("date", 1),
    )
    assert wc.filter_data(None, endswith="y") == (("cherry", 2), ("elderberry", 4))

    with pytest.raises(FilterError):
        wc.filter_data(None, endswith="r")


def test_filter_data_regex():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    # check for 2 of any letter
    assert wc.filter_data(None, regexp="e.*d.*.rr.*") == (("elderberry", 4),)
