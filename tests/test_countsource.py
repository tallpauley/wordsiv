import wordsiv
from wordsiv.models.wordcount import WordCountSource
from pathlib import Path

HERE = Path(__file__).parent.absolute()

wsv = wordsiv.WordSiv(limit_glyphs="HAMBURGERFONTSIVhamburgerfontsiv")
wsv.sources["test"] = WordCountSource(HERE / "data" / "count-source.txt")


def test_countsource_lc():
    assert wsv.word(source="test", model="prob", lc=True).islower()


def test_countsource_lc():
    assert wsv.word(source="test", model="prob", uc=True).isupper()


def test_countsource_cap():
    word = wsv.word(source="test", model="prob", cap=True)
    assert word[0].isupper() and word[1:].islower()


def test_countsource_cap_sent():
    sent = wsv.sentence(source="test", model="prob", cap_sent=True)
    assert sent[0].isupper() and sent[1:].islower()
