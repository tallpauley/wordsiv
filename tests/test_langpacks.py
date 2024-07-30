import pytest
import wordsiv
from wordsiv import WordSiv


def test_add_model_duplicate_error():
    ws = WordSiv(load_langpacks=False)
    ws.add_model("test_model", "model goes here", namespace="test")

    with pytest.raises(wordsiv.ModelDuplicateError):
        ws.add_model("test_model", "model goes here", namespace="test")


def test_get_model_not_found_error():
    ws = WordSiv(load_langpacks=False)
    with pytest.raises(wordsiv.ModelNotFoundError):
        ws.get_model("nonexistent_model")


def test_add_source_duplicate_error():
    ws = WordSiv(load_langpacks=False)
    ws.add_source("test_source", "source_goes_here", namespace="test")
    with pytest.raises(wordsiv.SourceDuplicateError):
        ws.add_source("test_source", "source_goes_here", namespace="test")


def test_get_model_multiple_models_found_error():
    ws = WordSiv(load_langpacks=False)
    ws.add_model("test_model", "model goes here", namespace="test")
    ws.add_model("test_model", "model goes here", namespace="test2")

    with pytest.raises(wordsiv.MultipleModelsFoundError):
        ws.get_model("test_model")
