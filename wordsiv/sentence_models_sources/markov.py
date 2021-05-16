from pathlib import Path
import os
import reprlib
import json
import markovify  # type: ignore
from markovify.chain import BEGIN, END  # type: ignore
from random import Random
import bisect
from itertools import accumulate
from functools import lru_cache
import copy
import time
from typing import Dict

from ..availableglyphs import AvailableGlyphs
from ..utilities import Hashabledict, HashabledictKeys
from ..utilities import has_glyphs
from ..source import BaseSource
from .base_sentence_model import BaseSentenceModel
from ..datawrapper import DataWrapper

#####################################################################################
###### SOURCE
#####################################################################################


class MarkovSource(BaseSource):
    """A source that is a compiled & serialized JSON Markovify.Text Object

    TODO Add test here
    """

    def __init__(self, data_file):
        self.data_file = data_file

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def data_wrap(self):
        return MarkovDataWrapper.from_json_file(self.data_file)


#####################################################################################
###### MODEL
#####################################################################################


class MarkovModel(BaseSentenceModel):
    _instances = {}  # type: ignore

    def __init__(self, markovify_text_data, available_glyphs, rand):

        self.markovify_text_data = markovify_text_data
        self.available_glyphs = available_glyphs
        self.rand = rand

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def markov_text(self):

        markov_text = SivText.from_dict(self.markovify_text_data.data)

        # TODO: less hacky way of feeding our rand object to chain??
        markov_text.chain.rand = self.rand
        markov_text.compile(inplace=True)

        return markov_text

    def sentence(self):
        """Generate a markov chain sentence"""

        # Ignore sent_len: handled by actual markov model
        return self.markov_text.make_sentence()

    def word(self, **kwargs):
        """No single word generation, just sentences and larger"""

        raise NotImplementedError

    def words(self, **kwargs):
        """No words generation, just sentences and larger"""

        raise NotImplementedError

    @classmethod
    def filter_and_create(cls, data, available_glyphs, font_info, rand, uc, lc):
        """
        returns a new instance if the data is new, otherwise returns a stored instance

        This is to make it easy on outside to make as many costly markovs as wanted, without
        passing around the objects from function to function
        """

        glyphs_tuple = (
            available_glyphs.glyphs_tuple if available_glyphs.limited else None
        )

        # filter chain_data by available
        data = filter_available(data, glyphs_tuple, uc=uc, lc=lc)

        # use chain data as hash to cache object instances
        # Note: in the case of markov chains, not only filtering the data is costly,
        # but also creating the model, since it requires compilation for performance
        # hence the caching of entire TextModels
        if data in cls._instances:
            return cls._instances[data]
        else:
            instance = cls(data, available_glyphs, rand)
            cls._instances[data] = instance
            return instance

    @classmethod
    def create_model(
        cls, data_wrap, available_glyphs, font_info, rand, uc=False, lc=False, **kwargs
    ):
        """Creates model, returning (model, **kwargs)"""

        model = cls.filter_and_create(
            data_wrap, available_glyphs, font_info, rand, uc, lc
        )
        return model, kwargs


#####################################################################################
###### DATA WRAPPER
#####################################################################################


class MarkovDataWrapper(DataWrapper):
    @classmethod
    def new_with_chain(self, markov_data, chain):
        obj = copy.copy(markov_data)
        obj.data["chain"] = chain
        obj.rehash()
        return obj

    @classmethod
    def from_json_file(cls, json_file):
        with open(json_file, "r") as f:
            # top level markovify.Text Dict needs to be hashed by keys and values,
            # since the keys are always the same
            data = Hashabledict(json.load(f))

        data["chain"] = json.loads(data["chain"])

        # make the chain Hashable.
        # No need to also hash counts: assuming keys will be unique enough
        def tuplify(state_follow):
            return tuple([tuple(state_follow[0]), HashabledictKeys(state_follow[1])])

        # make chain hashable
        data["chain"] = tuple(tuplify(state_follow) for state_follow in data["chain"])

        return cls(data)


#####################################################################################
###### FILTERS
#####################################################################################


@lru_cache(maxsize=None)
def filter_available(
    markov_data, available_glyphs_tuple, uc=False, lc=False, cap=False
):
    def uc_it(w):
        return w if w in (BEGIN, END) else w.upper()

    def lc_it(w):
        return w if w in (BEGIN, END) else w.lower()

    def cap_it(w):
        return w if w in (BEGIN, END) else w.capitalize()

    def nothing(w):
        return w

    if uc:
        case_function = uc_it
    elif lc:
        case_function = lc_it
    elif cap:
        case_function = cap_it
    else:
        # do nothing function if no cas is specified
        case_function = nothing

    chain = markov_data.data["chain"]

    # we produce a copy of the chain here
    filtered_chain = tuple(
        filter_available_gen(chain, available_glyphs_tuple, case_function)
    )

    return MarkovDataWrapper.new_with_chain(markov_data, filtered_chain)


# TODO: different filtering strategy in here, using an iterator, isn't congruent with word counts
def filter_available_gen(chain, available_glyphs_tuple, case_function):

    for state_list, follow in chain:
        # assume only using a state size of 1
        state_word = case_function(state_list[0])

        if state_word in (BEGIN, END) or has_glyphs(state_word, available_glyphs_tuple):
            filtered_follow_dict = HashabledictKeys(
                {
                    case_function(follow_word): prob
                    for follow_word, prob in follow.items()
                    if follow_word in (BEGIN, END)
                    or has_glyphs(case_function(follow_word), available_glyphs_tuple)
                }
            )

            yield tuple(
                [tuple([state_word]), filtered_follow_dict or Hashabledict({END: 1})]
            )


#####################################################################################
###### 3RD PARTY CLASS EXTENSIONS
#####################################################################################

# Redefine SivChain move() to use our custom hackily inserted rand module
class SivChain(markovify.Chain):
    def move(self, state):
        """
        Given a state, choose the next item at random.
        """
        if self.compiled:
            choices, cumdist = self.model[state]
        elif state == tuple([BEGIN] * self.state_size):
            choices = self.begin_choices
            cumdist = self.begin_cumdist
        else:
            choices, weights = zip(*self.model[state].items())
            cumdist = list(accumulate(weights))
        r = self.rand.random() * cumdist[-1]
        selection = choices[bisect.bisect(cumdist, r)]
        return selection

    # we add a special from_tuple to allow chain creation from hashable data (for caching)
    @classmethod
    def from_tuple(cls, obj):
        """
        Given an object like that created by `self.to_json`, but uses hashable structures
        return the corresponding markovify.Chain.
        """

        if isinstance(obj, tuple):
            rehydrated = dict((tuple(item[0]), item[1]) for item in obj)
        else:
            raise ValueError("Object should be a tuple")

        state_size = len(list(rehydrated.keys())[0])

        inst = cls(None, state_size, rehydrated)
        return inst


# SivText is extended just to make sure our own SivChain is used, with it's from_tuple() initialization
class SivText(markovify.Text):
    @classmethod
    def from_dict(cls, obj, **kwargs):
        return cls(
            None,
            state_size=obj["state_size"],
            chain=SivChain.from_tuple(obj["chain"]),
            parsed_sentences=obj.get("parsed_sentences"),
        )
