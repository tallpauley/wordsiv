import wordsiv
from wordsiv.sentence_models_sources import WordCountSource
from wordsiv.sentence_models_sources import MarkovSource
from pathlib import Path
import pytest

from test_source_modules import wctest, mkvtest

HERE = Path(__file__).parent.absolute()


@pytest.fixture(scope="session")
def wsv_no_source():
    w = wordsiv.WordSiv()
    return w


@pytest.fixture(scope="session")
def wsv_default():
    w = wordsiv.WordSiv()
    w.add_source_module(wctest)
    w.add_source_module(mkvtest)
    return w


def test_no_source(wsv_no_source):
    with pytest.raises(KeyError):
        wsv_no_source.word()


def test_default_not_exist(wsv_default):
    with pytest.raises(KeyError):
        wsv_default.set_default_source("not_exist")


@pytest.mark.parametrize("source_name", ("wctest", "mkvtest"))
def test_default_exists(wsv_default, source_name):
    wsv_default.set_default_source(source_name)
    assert type(wsv_default.sentence()) == str
