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


def has_function(obj, name):
    return hasattr(obj, name) and callable(getattr(obj, name))


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

    def load_sources(self):
        for s in installed_source_modules():
            self.sources.update(s.sources)
            self.pipelines.update(s.pipelines)

    def default(self, source, pipeline=None):
        self.sources["default"] = self.sources[source]

        # if no pipeline name specified, default pipeline is same as source name
        self.pipelines["default"] = self.pipelines[pipeline or source]

    def build_model(self, source=None, model=None, pipeline=None, **kwargs):
        """feeds source through filters and into a model which is returned"""

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

        # Pass the data to the model class to have it filter the data and return a model object
        model = model_class.filtered_model(
            source_obj.data, self.available_glyphs, self.font_info, self.rand, **kwargs
        )

        return model

    def sentence(
        self, sent_len=10, cap_sent=True, uc=False, lc=False, cap=False, **kwargs
    ):

        # build model at sentence level to check if it has sentence support
        model_obj = self.build_model(**kwargs, uc=uc, lc=lc, cap=cap)

        # Some models implement sentence themselves (like markov chains for instance)
        if has_function(model_obj, "sentence"):
            return model_obj.sentence(**kwargs, uc=uc, lc=lc, cap=cap)
        else:
            if uc or lc:
                first_word = self.word(uc=uc, lc=lc, cap=cap, **kwargs)
            else:
                # cap_sent parameter capitalizes first word if uc or lc isn't set
                first_word = self.word(cap=cap_sent, **kwargs)

            rest_of_sentence = " ".join(
                self.word(uc=uc, lc=lc, cap=cap, **kwargs) for _ in range(sent_len - 1)
            )
            return " ".join((first_word, rest_of_sentence))

    def sentences(self, num_sents=10, sent_len=None, **kwargs):

        # build model to see if it can do sentences, or else add our own sentence termination
        if has_function(self.build_model(**kwargs), "sentence"):
            sep = [""]
        else:
            sep = [s for s in ".?" if self.available_glyphs.have_glyphs(s)]

        def rand_sep(options):
            if options:
                return self.rand.choice(options) + " "
            else:
                return " "

        return "".join(
            (self.sentence(**kwargs) + rand_sep(sep) for _ in range(num_sents))
        )

    # TODO eliminate building model here?
    def paragraphs(self, num_paras=5, num_sents=7, model=None, **kwargs):
        if isinstance(model, str) or not model:
            model_obj = self.build_model(model=model, **kwargs)
        else:
            model_obj = model

        return "\n\n".join(
            self.sentences(model=model_obj, num_sents=num_sents, **kwargs)
            for _ in range(num_paras)
        )

    def word(self, model=None, source=None, **kwargs):
        # if model is a string, build a model, else use as is
        if isinstance(model, str) or not model:
            model = self.build_model(model=model, source=source, **kwargs)

        return model.word()

    def words(self, num_words=10, model=None, **kwargs):
        if isinstance(model, str) or not model:
            model_obj = self.build_model(model=model, **kwargs)
        else:
            model_obj = model

        return "\n".join(self.word(model=model_obj, **kwargs) for _ in range(num_words))
