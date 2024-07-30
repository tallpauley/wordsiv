from wordsiv.sources import WordCountSource
import pytest

import pytest
from wordsiv.sources import WordFilterError, SourceEmptyError, SourceFormatError


def test_wordcountsource_no_data():
    test_data = ""
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(SourceEmptyError):
        wc.filter_data(None)


def test_wordcountsource_bad_format():
    test_data = "123 123"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(SourceFormatError):
        wc.filter_data(None)


def test_wordcountsource_no_counts():
    test_data = "apple\nbanana\ncherry\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    assert wc.filter_data(None) == (("apple", 1), ("banana", 1), ("cherry", 1))


def test_filter_data_empty_glyphs():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(WordFilterError):
        wc.filter_data("xyz")


def test_filter_data_empty_word_length():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(WordFilterError):
        wc.filter_data(None, min_wl=10)


def test_filter_data_empty_contains():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(WordFilterError):
        wc.filter_data(None, contains="xyz")


def test_filter_data_empty_startswith():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(WordFilterError):
        wc.filter_data(None, startswith="x")


def test_filter_data_empty_endswith():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(WordFilterError):
        wc.filter_data(None, endswith="x")


def test_filter_data_empty_regexp():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    with pytest.raises(WordFilterError):
        wc.filter_data(None, regexp="x+")


def test_filter_data():
    test_data = "apple\t5\nApple\t5\nAPPLE\t5"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    # Test with limited glyphs
    assert wc.filter_data("aple") == (("apple", 5),)
    assert wc.filter_data("Aple") == (("Apple", 5),)
    assert wc.filter_data("APLE") == (("APPLE", 5),)


# test casing
def test_filter_data_case():
    test_data = "apple\t5\nBanana\t3\nPeACH\t2\nGRAPE\t1"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    # all glyphs available
    assert wc.filter_data(None, case="cap") == (("Apple", 5), ("Banana", 3))
    assert wc.filter_data(None, case="lc") == (("apple", 5),)
    assert wc.filter_data(None, case="uc") == (
        ("APPLE", 5),
        ("BANANA", 3),
        ("PEACH", 2),
        ("GRAPE", 1),
    )

    # limited glyphs and case specified
    assert wc.filter_data("Aple", case="cap") == (("Apple", 5),)
    assert wc.filter_data("apple", case="lc") == (("apple", 5),)
    assert wc.filter_data("APLEPCH", case="uc") == (("APPLE", 5), ("PEACH", 2))

    # limited glyphs, no UC glyphs available
    with pytest.raises(WordFilterError):
        wc.filter_data("aple", case="cap")

    with pytest.raises(WordFilterError):
        wc.filter_data("grape", case="uc")

    # limited glyphs, no LC glyphs available
    with pytest.raises(WordFilterError):
        wc.filter_data("APLE", case="lc")


def test_filter_data_wl():
    test_data = "apple\t10\nbanana\t5\njoe\t2"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    assert wc.filter_data(None, wl=3) == (("joe", 2),)
    assert wc.filter_data(None, min_wl=3) == (("apple", 10), ("banana", 5), ("joe", 2))
    assert wc.filter_data(None, min_wl=4) == (("apple", 10), ("banana", 5))
    assert wc.filter_data(None, min_wl=6) == (("banana", 5),)
    assert wc.filter_data(None, max_wl=3) == (("joe", 2),)


def test_filter_data_startswith_endswith_contains():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    assert wc.filter_data(None, startswith="a") == (("apple", 5),)
    assert wc.filter_data(None, contains="a") == (
        ("apple", 5),
        ("banana", 3),
        ("date", 1),
    )
    assert wc.filter_data(None, endswith="y") == (("cherry", 2), ("elderberry", 4))

    with pytest.raises(WordFilterError):
        wc.filter_data(None, endswith="r")


def test_filter_data_regex():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4\n"
    wc = WordCountSource("fake/path", meta={"bicameral": "True"}, test_data=test_data)

    # check for 2 of any letter
    assert wc.filter_data(None, regexp="e.*d.*.rr.*") == (("elderberry", 4),)
