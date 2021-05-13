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
from .models.wordcount import (
    WordCountSource,
    ProbabilityModel,
    TopModel,
    RandomModel,
)
from .utilities import installed_source_modules
from .models.markov import MarkovSource, MarkovModel


class WordSiv:
    def __init__(self, font_file=None, limit_glyphs=None, seed=1):

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
        self.pipelines = {}

        # populate pipelines and sources from data source packages
        self.load_sources()

        self.model_classes = {
            "prob": ProbabilityModel,
            "top": TopModel,
            "rand": RandomModel,
            "markov": MarkovModel,
        }

    def add_source_module(self, source_module):
        self.sources.update(source_module.sources)
        self.pipelines.update(source_module.pipelines)

    def load_sources(self):
        for sm in installed_source_modules():
            self.add_source_module(sm)

    def set_default(self, source, pipeline=None):
        self.sources["default"] = self.sources[source]

        # if no pipeline name specified, default pipeline is same as source name
        self.pipelines["default"] = self.pipelines[pipeline or source]

    def select_source_model(self, source=None, model=None, pipeline=None, **kwargs):
        """Select source object and model class

        Args:
            source: name to lookup in self.sources
            model: name to lookup in self.model_classes
            source: name to lookup in self.pipelines

        Returns:
            A tuple with (source_object, model_class)
        """

        if not self.sources:
            raise KeyError("No data source packages loaded!")

        source_name = source or "default"

        # do pipeline if specified, or if neither source nor model are defined
        if pipeline or (not source and not model):
            pipeline_name = pipeline or "default"
            pipeline = self.pipelines[pipeline_name]
            model_class = pipeline["model_class"]
            source_obj = pipeline["source"]
        else:
            # if no source defined, use default source
            source_obj = self.sources[source or "default"]

            # we assume a model is always specified if a pipeline is not
            # a default source makes some sense since the user explicitly loaded it
            # a default model doesn't really make sense, outside of pipelines which
            #     pair together source and model
            model_class = self.model_classes[model]

        return source_obj, model_class

    def create_model_and_run(
        self, method, source=None, model=None, pipeline=None, **kwargs
    ):
        """creates a model, and runs a method on it to produce text"""

        source_obj, model_class = self.select_source_model(
            source=source, model=model, pipeline=pipeline, **kwargs
        )

        return model_class.create_and_run(
            method,
            source_obj.data_wrap,
            self.available_glyphs,
            self.font_info,
            self.rand,
            **kwargs
        )

    def word(self, source=None, model=None, pipeline=None, **kwargs):
        return self.create_model_and_run("word", source, model, pipeline, **kwargs)

    def words(self, source=None, model=None, pipeline=None, **kwargs):
        return self.create_model_and_run("words", source, model, pipeline, **kwargs)

    def sentence(self, source=None, model=None, pipeline=None, **kwargs):
        return self.create_model_and_run("sentence", source, model, pipeline, **kwargs)

    def sentences(self, source=None, model=None, pipeline=None, **kwargs):
        return self.create_model_and_run("sentences", source, model, pipeline, **kwargs)

    def paragraph(self, source=None, model=None, pipeline=None, **kwargs):
        return self.create_model_and_run("paragraph", source, model, pipeline, **kwargs)

    def paragraphs(self, source=None, model=None, pipeline=None, **kwargs):
        return self.create_model_and_run(
            "paragraphs", source, model, pipeline, **kwargs
        )

    def text(self, source=None, model=None, pipeline=None, **kwargs):
        return self.create_model_and_run("text", source, model, pipeline, **kwargs)
