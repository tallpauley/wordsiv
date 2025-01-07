from wordsiv import Vocab, FilterError
from wordsiv._vocab import VocabFormatError, VocabEmptyError
import pytest


def test_vocab_no_data():
    test_data = ""
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(VocabEmptyError):
        vc.wordcount


def test_vocab_no_data_no_data_file_raises_valueerror():
    with pytest.raises(ValueError):
        Vocab(bicameral=True, lang="en")


def test_vocab_data_and_data_file_raises_valueerror():
    with pytest.raises(ValueError):
        Vocab(bicameral=True, lang="en", data="test", data_file="test")


def test_vocab_bad_format():
    test_data = "123\t123"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(VocabFormatError):
        vc.wordcount


def test_vocab_no_counts():
    test_data = "apple\nbanana\ncherry"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.wordcount == (("apple", 1), ("banana", 1), ("cherry", 1))


def test_vocab_filter_glyphs_raises_filtererror():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(glyphs="xyz")


def test_vocab_filter_wl_raises_filtererror():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, min_wl=10)


def test_vocab_filter_contains_raises_filtererror():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, contains="xyz")


def test_vocab_filter_startswith_raises_filtererror():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, startswith="x")


def test_vocab_filter_endswith_raises_filtererror():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, endswith="x")


def test_vocab_filter_regexp_raises_filtererror():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, regexp="x+")


def test_vocab_filter_glyphs_any_exact():
    test_data = "grape\t6\napple\t5\nApple\t4\nBart\t3\nBART\t2\nDDoS\t1"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # if we have the letters to spell the word exactly as it is in the vc, we'll match it
    assert vc.filter("aple") == (("apple", 5),)
    assert vc.filter("BARTDoS") == (("BART", 2), ("DDoS", 1))


def test_vocab_filter_glyphs_any_cap_transform():
    test_data = "grape\t6\napple\t5\nApple\t4\nBart\t3\nBART\t2\nDDoS\t1"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # if no exact matches for the glyph set, we'll match Cap and UC of lc vc words
    assert vc.filter("GRAPEgrape") == (("grape", 6),)
    assert vc.filter("Grape") == (("Grape", 6),)


def test_vocab_filter_glyphs_any_uc_transform():
    test_data = "grape\t6\napple\t5\nApple\t4\nBart\t3\nBART\t2\nDDoS\t1"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter("GRAPE") == (("GRAPE", 6),)
    assert vc.filter("APLE") == (("APPLE", 5), ("APPLE", 4))


def test_vocab_filter_glyphs_any_uc_transform_wl():
    test_data = "Paris\t6\nPA\t5"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # This function tests a specific characteristic of case='any'
    # - the case filter was previously at the beginning of the filter pipeline
    # - the case filter would return just 'PA', so it wouldn't need to try to expand
    # results by uppercasing `Paris`
    # - the word length filter would then filter out 'PA'
    # The solution has been to move the case filter to the end of the filter pipeline
    # for the 'any' case, so that if any filter (like wl) is restrictive, we can still
    # expand our case filter at the end
    assert vc.filter("PARIS", min_wl=5) == (("PARIS", 6),)


def test_vocab_filter_glyphs_any_no_lc_transform_raises_filtererror():
    test_data = "grape\t6\napple\t5\nApple\t4\nBart\t3\nBART\t2\nDDoS\t1"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # Capitalized, UC, CamelCaps words will not be lowercased,
    # since lowercasing an acronym or proper noun is often incorrect
    with pytest.raises(FilterError):
        vc.filter("bartdos")


def test_vocab_filter_case_raises_value_error():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(ValueError):
        vc.filter(None, case="fake")


def test_vocab_filter_case_lc():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, case="lc") == (("grape", 1), ("apple", 2))


def test_vocab_filter_case_lc_force():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, case="lc_force") == (
        ("grape", 1),
        ("apple", 2),
        ("apple", 3),
        ("bart", 4),
        ("bart", 5),
        ("ddos", 6),
    )


def test_vocab_filter_case_uc():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, case="uc") == (
        ("GRAPE", 1),
        ("APPLE", 2),
        ("APPLE", 3),
        ("BART", 4),
        ("BART", 5),
        ("DDOS", 6),
    )


def test_vocab_filter_case_cap():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, case="cap") == (
        ("Grape", 1),
        ("Apple", 2),
        ("Apple", 3),
        ("Bart", 4),
    )


def test_vocab_filter_case_cap_force():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, case="cap_force") == (
        ("Grape", 1),
        ("Apple", 2),
        ("Apple", 3),
        ("Bart", 4),
        ("Bart", 5),
        ("Ddos", 6),
    )


def test_vocab_filter_glyphs_case():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # simple cases
    assert vc.filter(glyphs="aple", case="lc") == (("apple", 2),)
    assert vc.filter(glyphs="Aple", case="cap") == (("Apple", 2), ("Apple", 3))
    assert vc.filter(glyphs="APPLE", case="uc") == (("APPLE", 2), ("APPLE", 3))
    assert vc.filter(glyphs="BART", case="uc") == (("BART", 4), ("BART", 5))
    assert vc.filter(glyphs="DDOS", case="uc") == (("DDOS", 6),)


def test_vocab_filter_glyphs_case_raises_filtererror():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(glyphs="bart", case="lc")

    with pytest.raises(FilterError):
        vc.filter(glyphs="Ddos", case="cap")


def test_vocab_filter_glyphs_case_lc_force():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(glyphs="bart", case="lc_force") == (
        ("bart", 4),
        ("bart", 5),
    )


def test_vocab_filter_glyphs_case_cap_force():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(glyphs="Ddos", case="cap_force") == (("Ddos", 6),)


def test_vocab_filter_wl():
    test_data = "apple\t10\nbanana\t5\njoe\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, wl=3) == (("joe", 2),)
    assert vc.filter(None, min_wl=3) == (("apple", 10), ("banana", 5), ("joe", 2))
    assert vc.filter(None, min_wl=4) == (("apple", 10), ("banana", 5))
    assert vc.filter(None, min_wl=6) == (("banana", 5),)
    assert vc.filter(None, max_wl=3) == (("joe", 2),)


def test_vocab_filter_startswith():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, startswith="a") == (("apple", 5),)


def test_vocab_filter_contains():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, contains="a") == (
        ("apple", 5),
        ("banana", 3),
        ("date", 1),
    )


def test_vocab_filter_inner():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, inner="a") == (
        ("banana", 3),
        ("date", 1),
    )


def test_vocab_filter_endswith():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, endswith="y") == (("cherry", 2), ("elderberry", 4))


def test_vocab_filter_regex():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # check for 2 of any letter
    assert vc.filter(None, regexp="e.*d.*.rr.*") == (("elderberry", 4),)
