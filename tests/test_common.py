import wordsiv
from wordsiv.models.wordcount import WordCountSource
from wordsiv.models.markov import MarkovSource
from pathlib import Path
import pytest

from test_source_modules import wctest, mktest

HERE = Path(__file__).parent.absolute()
LIMITED_CHARS = "HAMBURGERFONTSIVhamburgerfontsiv"


@pytest.fixture(scope="session")
def wsv_no_source():
    w = wordsiv.WordSiv()
    return w


@pytest.fixture(scope="session")
def wsv_default():
    w = wordsiv.WordSiv()
    w.add_source_module(wctest)
    w.add_source_module(mktest)
    return w


def test_no_source(wsv_no_source):
    with pytest.raises(KeyError):
        wsv_no_source.word()


def test_default_not_exist(wsv_default):
    with pytest.raises(KeyError):
        wsv_default.set_default("not_exist")


def test_default_exists(wsv_default):
    wsv_default.set_default("wctest")
    assert type(wsv_default.word()) == str