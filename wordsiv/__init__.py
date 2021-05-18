"""Wordsiv is a Python library for generating text with a limited character set."""

import string
from random import Random
import json
from functools import partial
import pprint
import importlib
import pkg_resources

from .fontinfo import FontInfo
from .availableglyphs import AvailableGlyphs
from .sentence_models_sources import (
    WordCountSource,
    RandomModel,
    SequentialModel,
    MarkovSource,
    MarkovModel,
)
from .utilities import installed_source_modules

DEFAULT_SEED = 11
DEFAULT_MIN_PARA_LEN = 4
DEFAULT_MAX_PARA_LEN = 7


class WordSiv:
    def __init__(self, font_file=None, limit_glyphs=None, seed=DEFAULT_SEED):

        # set up available characters
        self.font_info = FontInfo(font_file) if font_file else None

        if font_file:
            font_chars = self.font_info.characters

            if limit_glyphs:
                glyphs = sorted(c for c in font_chars if c in limit_glyphs)
            else:
                glyphs = font_chars
        else:
            glyphs = limit_glyphs

        self.available_glyphs = AvailableGlyphs(limit_glyphs=glyphs)

        # create shared Random() object
        self.rand = Random(seed)

        self.sources = {}
        self.default_source_name = None
        self.default_model_class_name = None

        # populate sources from data source packages
        self.load_sources()

        self.model_classes = {
            "rand": RandomModel,
            "seq": SequentialModel,
            "mkv": MarkovModel,
        }

    def add_source_module(self, source_module):
        for source_name, params in source_module.sources.items():
            if source_name not in self.sources:
                self.sources[source_name] = params
            else:
                raise KeyError(f"Source {source_name} is already installed!")

    def load_sources(self):
        for sm in installed_source_modules():
            self.add_source_module(sm)

    def set_default_source(self, source, model=None):
        if source in self.sources:
            self.default_source_name = source
        else:
            raise KeyError(f"No source installed with name {source}!")
        if model:
            self.default_model_class_name = model

    def select_source_model(self, source=None, model=None):
        """Select source object and model class

        Args:
            source: name to lookup in self.sources
            model: name to lookup in self.model_classes

        Returns:
            A tuple with (source_object, model_class)
        """

        if not self.sources:
            raise KeyError("No data source packages installed!")

        source_name = source or self.default_source_name
        source_obj = self.sources[source_name]["source"]

        if model:
            model_class = self.model_classes[model]
        elif self.default_model_class_name:
            model_class = self.model_classes[self.default_model_class_name]
        else:
            model_class = self.sources[source_name]["default_model_class"]

        return source_obj, model_class

    def create_model(self, source=None, model=None, **kwargs):
        """creates a model, and returns model along with kwargs for function call"""

        source_obj, model_class = self.select_source_model(source=source, model=model)

        return model_class.create_model(
            source_obj.data_wrap,
            self.available_glyphs,
            self.font_info,
            self.rand,
            source_obj.meta["lang"],
            **kwargs,
        )

    def word(self, source=None, model=None, **kwargs):
        model, params = self.create_model(source, model, **kwargs)
        return model.word(**params)

    def words(self, source=None, model=None, **kwargs):
        model, params = self.create_model(source, model, **kwargs)
        return model.words(**params)

    def sentence(self, source=None, model=None, **kwargs):
        model, params = self.create_model(source, model, **kwargs)
        return model.sentence(**params)

    def sentences(
        self,
        min_para_len=DEFAULT_MIN_PARA_LEN,
        max_para_len=DEFAULT_MAX_PARA_LEN,
        para_len=None,
        source=None,
        model=None,
        **kwargs,
    ):
        """Return a list of sentence strings"""

        if not para_len:
            para_len = self.rand.randint(min_para_len, max_para_len)

        return [
            self.sentence(source=source, model=model, **kwargs) for _ in range(para_len)
        ]

    def paragraph(self, sent_sep=" ", source=None, model=None, **kwargs):
        """Return a paragraph string"""
        return sent_sep.join(self.sentences(source=source, model=model, **kwargs))

    def paragraphs(
        self,
        num_paras=3,
        source=None,
        model=None,
        **kwargs,
    ):
        """Return a list of paragraphs"""
        return [
            self.paragraph(source=source, model=model, **kwargs)
            for _ in range(num_paras)
        ]

    def text(self, para_sep="\n\n", source=None, model=None, **kwargs):
        """Return a string of multiple paragraphs seperated by par_sep"""
        return para_sep.join(self.paragraphs(source=source, model=model, **kwargs))
