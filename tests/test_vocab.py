from wordsiv import Vocab, VocabEmptyError, VocabFormatError, FilterError
import pytest


def test_vc_no_data():
    test_data = ""
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(VocabEmptyError):
        vc.wordcount


def test_vc_bad_format():
    test_data = "123\t123"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(VocabFormatError):
        vc.wordcount


def test_vc_no_counts():
    test_data = "apple\nbanana\ncherry"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.wordcount == [("apple", 1), ("banana", 1), ("cherry", 1)]


def test_filter_wrong_glyphs():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(glyphs="xyz")


def test_filter_empty_word_length():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, min_wl=10)


def test_filter_empty_contains():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, contains="xyz")


def test_filter_empty_startswith():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, startswith="x")


def test_filter_empty_endswith():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, endswith="x")


def test_filter_empty_regexp():
    test_data = "apple\t5\nbanana\t3\ncherry\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    with pytest.raises(FilterError):
        vc.filter(None, regexp="x+")


def test_filter_glyphs():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # if we have the letters to spell the word exactly as it is in the vc, we'll match it
    assert vc.filter("aple") == (("apple", 2),)
    assert vc.filter("BARTDoS") == (("BART", 5), ("DDoS", 6))

    # if no exact matches for the glyph set, we'll match Cap and UC of lc vc words
    assert vc.filter("GRAPEgrape") == (("grape", 1),)
    assert vc.filter("Grape") == (("Grape", 1),)
    assert vc.filter("GRAPE") == (("GRAPE", 1),)
    assert vc.filter("APLE") == (("APPLE", 2), ("APPLE", 3))

    # Capitalized, UC, CamelCaps words will not be lowercased,
    # since lowercasing an acronym or proper noun is often incorrect, however...
    with pytest.raises(FilterError):
        vc.filter("bartdos")


def test_filter_case():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # if you do a fake case it'll throw a ValueError
    with pytest.raises(ValueError):
        vc.filter(None, case="fake")

    # with case='lc' and glyph = None, we'll just match words that are already lowercase
    assert vc.filter(None, case="lc") == (("grape", 1), ("apple", 2))

    # unless, you want to force them lowercase
    assert vc.filter(None, case="lc_force") == (
        ("grape", 1),
        ("apple", 2),
        ("apple", 3),
        ("bart", 4),
        ("bart", 5),
        ("ddos", 6),
    )

    # with case='uc', it assumes any word can be uppercased
    assert vc.filter(None, case="uc") == (
        ("GRAPE", 1),
        ("APPLE", 2),
        ("APPLE", 3),
        ("BART", 4),
        ("BART", 5),
        ("DDOS", 6),
    )

    # with case='cap', by default it only matches lowercase and capitalized words in the vc
    assert vc.filter(None, case="cap") == (
        ("Grape", 1),
        ("Apple", 2),
        ("Apple", 3),
        ("Bart", 4),
    )

    # unless you want to force it with 'cap_force
    assert vc.filter(None, case="cap_force") == (
        ("Grape", 1),
        ("Apple", 2),
        ("Apple", 3),
        ("Bart", 4),
        ("Bart", 5),
        ("Ddos", 6),
    )


def test_filter_glyphs_case():
    test_data = "grape\t1\napple\t2\nApple\t3\nBart\t4\nBART\t5\nDDoS\t6"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # simple cases
    assert vc.filter(glyphs="aple", case="lc") == (("apple", 2),)
    assert vc.filter(glyphs="Aple", case="cap") == (("Apple", 2), ("Apple", 3))
    assert vc.filter(glyphs="APPLE", case="uc") == (("APPLE", 2), ("APPLE", 3))
    assert vc.filter(glyphs="BART", case="uc") == (("BART", 4), ("BART", 5))
    assert vc.filter(glyphs="DDOS", case="uc") == (("DDOS", 6),)

    # cases with no matches...
    with pytest.raises(FilterError):
        vc.filter(glyphs="bart", case="lc")

    with pytest.raises(FilterError):
        vc.filter(glyphs="Ddos", case="cap")

    # unless you want to force lc
    assert vc.filter(glyphs="bart", case="lc_force") == (
        ("bart", 4),
        ("bart", 5),
    )
    # or force cap
    assert vc.filter(glyphs="Ddos", case="cap_force") == (("Ddos", 6),)


def test_filter_wl():
    test_data = "apple\t10\nbanana\t5\njoe\t2"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, wl=3) == (("joe", 2),)
    assert vc.filter(None, min_wl=3) == (("apple", 10), ("banana", 5), ("joe", 2))
    assert vc.filter(None, min_wl=4) == (("apple", 10), ("banana", 5))
    assert vc.filter(None, min_wl=6) == (("banana", 5),)
    assert vc.filter(None, max_wl=3) == (("joe", 2),)


def test_filter_startswith_endswith_contains():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    assert vc.filter(None, startswith="a") == (("apple", 5),)
    assert vc.filter(None, contains="a") == (
        ("apple", 5),
        ("banana", 3),
        ("date", 1),
    )
    assert vc.filter(None, endswith="y") == (("cherry", 2), ("elderberry", 4))

    with pytest.raises(FilterError):
        vc.filter(None, endswith="r")


def test_filter_regex():
    test_data = "apple\t5\nbanana\t3\ncherry\t2\ndate\t1\nelderberry\t4"
    vc = Vocab(bicameral=True, lang="en", data=test_data)

    # check for 2 of any letter
    assert vc.filter(None, regexp="e.*d.*.rr.*") == (("elderberry", 4),)
