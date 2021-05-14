from functools import lru_cache
from collections import OrderedDict
from itertools import islice
import random
import reprlib
from pathlib import Path
import os
import re
import json

from ..utilities import has_glyphs, Hashabledict, HashabledictKeys
from ..source import BaseSource
from ..base_models import BaseCachedWordModel, BaseWordTextModel
from ..datawrapper import DataWrapper, unwrap

BIG_NUM = 100000

TEST_MODULES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / "../../tests/test_source_modules"
)

#####################################################################################
###### UTILITY
######################################################################################


def zip_tuple(a_tuple):
    """Zip a tuple of tuple pairs into a tuple (cached)

    >>> zip_tuple((('hi', 123), ('hello', 321)))
    (('hi', 'hello'), (123, 321))
    """

    tuple1, tuple2 = zip(*a_tuple)
    return tuple1, tuple2


#####################################################################################
###### SOURCE
######################################################################################


def stream_file_tuples(file, lines=None):
    """Yield a tuple ('myword', 123) for each line of a file like 'myword 123'"""

    with open(file, "r") as f:
        lc = 0
        for line in f:
            word, count = re.split("\s+", line.strip())
            yield (word, int(count))

            if lines:
                if lc >= lines:
                    break

                lc += 1


class WordCountSource(BaseSource):
    """A Source that expects a txt file with words and counts

    file looks like this: "koala 235\ncobra 123\n"

    >>> obj = WordCountSource( \
            TEST_MODULES_DIR / "wctest/data/count-source.txt", lines=3)
    >>> obj.data_wrap.data
    (('gather', 94), ('to', 119), ('sublimedirectory', 204), ('sublimedirectory', 12))
    """

    def __init__(self, data_file, lines=None):
        self.data_file = data_file
        self.lines = lines

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def data_wrap(self):
        """for a WordCountSource, data is a tuple of tuples"""

        return DataWrapper(tuple(stream_file_tuples(self.data_file, self.lines)))


#####################################################################################
###### WORDTEXT MODELS
#####################################################################################


class ProbabilityModel(BaseWordTextModel):
    """TextModel which randomly selects words (probability distribution from counts)"""

    def word(self, **kwargs):
        """Randomly select a word with proabability distribution defined by word counts

        Keyword Args:
            uc (bool): Uppercase word
            lc (bool): Lowercase word
            cap (bool): Capitalize word
            num_top (int): Limit number of words drawn from
            min_wl (int): Minimum word length,
            max_wl (int): Maximum word length,
            wl (int): Word length,
            min_width (int): Minimum approximate rendered word width,
            max_width (int): Maximum approximate rendered word width,
            width (int): Approximate rendered word width
        """

        filtered_data_wrap = filter_data(
            self.data_wrap, self.available_glyphs, self.font_info, **kwargs
        )

        return ProbabilityWordModel.create(filtered_data_wrap, self.rand).word(**kwargs)


class TopModel(BaseWordTextModel):
    """TextModel which returns words sequentially in the order of the source data"""

    def word(self, **kwargs):
        """

        Keyword Args:
            uc (bool): Uppercase word
            lc (bool): Lowercase word
            cap (bool): Capitalize word
            num_top (int): Limit number of words drawn from
            min_wl (int): Minimum word length,
            max_wl (int): Maximum word length,
            wl (int): Word length,
            min_width (int): Minimum approximate rendered word width,
            max_width (int): Maximum approximate rendered word width,
            width (int): Approximate rendered word width
        """

        filtered_data_wrap = filter_data(
            self.data_wrap, self.available_glyphs, self.font_info, **kwargs
        )

        return TopWordModel.create(filtered_data_wrap, self.rand).word(**kwargs)


class RandomModel(BaseWordTextModel):
    """TextModel which randomly selects words (equal probability for all words)"""

    def word(self, **kwargs):
        """Randomly select a word with equal probability for all words

        Keyword Args:
            uc (bool): Uppercase word
            lc (bool): Lowercase word
            cap (bool): Capitalize word
            num_top (int): Limit number of words drawn from
            min_wl (int): Minimum word length,
            max_wl (int): Maximum word length,
            wl (int): Word length,
            min_width (int): Minimum approximate rendered word width,
            max_width (int): Maximum approximate rendered word width,
            width (int): Approximate rendered word width
        """

        filtered_data_wrap = filter_data(
            self.data_wrap, self.available_glyphs, self.font_info, **kwargs
        )

        return RandomWordModel.create(filtered_data_wrap, self.rand).word(**kwargs)


#####################################################################################
###### WORD MODELS
#####################################################################################


class ProbabilityWordModel(BaseCachedWordModel):
    """
    A WordModel that uses occurences counts to generate words
    """

    def __init__(self, data_wrap, rand):

        self.rand = rand
        self.word_list, self.counts = zip_tuple(data_wrap.data)

    def word(self, **kwargs):
        return self.rand.choices(self.word_list, k=1, weights=self.counts)[0]


class TopWordModel(BaseCachedWordModel):
    """
    A WordModel that spits out the words sequentially

    Useful for things like trigrams, where you often just
    want to print out the top few
    """

    def __init__(self, data_wrap, rand):

        self.rand = rand
        # don't need counts
        self.word_list, _ = zip_tuple(data_wrap.data)

        self.reset()

    def reset(self):
        self.iterator = self.new_iterator()

    def new_iterator(self):
        return iter(self.word_list)

    def word(self, **kwargs):
        return next(self.iterator)


class RandomWordModel(BaseCachedWordModel):
    """
    A WordModel which picks words completely randomly
    """

    def __init__(self, data_wrap, rand):

        self.rand = rand
        # don't need counts
        self.word_list, _ = zip_tuple(data_wrap.data)

    def word(self, **kwargs):
        return self.rand.choice(self.word_list)


#####################################################################################
###### FILTERS
#####################################################################################


def filter_data(
    data_wrap,
    available_glyphs,
    font_info,
    num_top=None,
    uc=False,
    lc=False,
    cap=False,
    min_wl=0,
    max_wl=BIG_NUM,
    wl=None,
    min_width=0,
    max_width=BIG_NUM,
    width=None,
):

    dw = data_wrap

    glyphs_tuple = available_glyphs.glyphs_tuple if available_glyphs.limited else None

    if uc:
        dw = uc_filter(dw, glyphs_tuple)
    elif lc:
        dw = lc_filter(dw, glyphs_tuple)
    elif cap:
        dw = cap_filter(dw, glyphs_tuple)
    else:
        dw = available_filter(dw, glyphs_tuple)

    if min_wl or max_wl != BIG_NUM or wl:
        dw = length_filter(dw, min_wl, max_wl, wl)

    if font_info:
        if min_width or max_width != BIG_NUM or width:
            dw = width_filter(
                dw, font_info.char_widths_tuple(), min_width, max_width, width
            )

    if num_top:
        dw = top_filter(dw, num_top)

    return dw


@unwrap(DataWrapper)
@lru_cache(maxsize=None)
def top_filter(words_count, num_top=1000):
    """
    return top items from a given words_count tuple

    Example:
    >>> data = (("Duck", 1), ("pig", 2), ("thing", 3))
    >>> top_filter(data, 2)
    (('Duck', 1), ('pig', 2))
    """
    return tuple(islice(words_count, num_top))


@unwrap(DataWrapper)
@lru_cache(maxsize=None)
def available_filter(words_count, available_glyphs_string):
    """
    return tuple of unique words that have all chars in available_glyph_list
    words_count is in format (("word", 123), ("word2", 34))

    Example:
    >>> available_filter((("Duck", 1), ("pig", 2), ("PIG", 3), ("goose", 4), ("LamB", 5)), "DuckPIG")
    (('Duck', 1), ('PIG', 3))
    """

    return tuple(
        tuple((word, count))
        for word, count in words_count
        if has_glyphs(word, available_glyphs_string)
    )


@unwrap(DataWrapper)
@lru_cache(maxsize=None)
def lc_filter(words_count, available_glyphs_string):
    """
    Lowercase words and return tuple of unique words that have all chars in available_glyph_list
    words_count is in format (("word", 123), ("word2", 34))
    If there are duplicate words with multiple casings in words_count, keep the first count

    Example:
    >>> lc_filter((("Duck", 1), ("pig", 2), ("PIG", 3), ("goose", 4), ("LamB", 5)), "lambpig")
    (('pig', 2), ('lamb', 5))
    """

    output = OrderedDict()
    for word, count in words_count:
        word_lc = word.lower()
        if has_glyphs(word_lc, available_glyphs_string) and word_lc not in output:
            output[word_lc] = count

    return tuple(output.items())


@unwrap(DataWrapper)
@lru_cache(maxsize=None)
def uc_filter(words_count, available_glyphs_string):
    """
    Uppercase words and return tuple of unique words that have all chars in available_glyph_list
    words_count is in format (("word", 123), ("word2", 34))
    If there are duplicate words with multiple casings in words_count, keep the first count

    Example:
    >>> uc_filter((("Duck", 1), ("pig", 2), ("PIG", 3), ("goose", 4), ("LamB", 5)), "LAMBPIG")
    (('PIG', 2), ('LAMB', 5))
    """

    output = OrderedDict()
    for word, count in words_count:
        word_uc = word.upper()
        if has_glyphs(word_uc, available_glyphs_string) and word_uc not in output:
            output[word_uc] = count

    return tuple(output.items())


@unwrap(DataWrapper)
@lru_cache(maxsize=None)
def cap_filter(words_count, available_glyphs_string):
    """
    Uppercase words and return tuple of unique words that have all chars in available_glyph_list
    words_count is in format (("word", 123), ("word2", 34))
    If there are duplicate words with multiple casings in words_count, keep the first count

    Example:
    >>> cap_filter((("Duck", 1), ("pig", 2), ("PIG", 3), ("goose", 4), ("LamB", 5)), "LambPig")
    (('Pig', 2), ('Lamb', 5))
    """

    output = OrderedDict()
    for word, count in words_count:
        word_cap = word.capitalize()
        if has_glyphs(word_cap, available_glyphs_string) and word_cap not in output:
            output[word_cap] = count

    return tuple(output.items())


@unwrap(DataWrapper)
@lru_cache(maxsize=None)
def length_filter(words_count, min_wl=0, max_wl=BIG_NUM, wl=None):
    """
    Filters by number of characters in words

    Example:
    """

    if min_wl or (max_wl < BIG_NUM):
        return tuple(
            (word, count)
            for word, count in words_count
            if min_wl <= len(word) <= max_wl
        )
    elif wl:
        return tuple((word, count) for word, count in words_count if wl == len(word))
    else:
        return words_count


@unwrap(DataWrapper)
@lru_cache(maxsize=None)
def width_filter(words_count, char_widths, min_width=0, max_width=BIG_NUM, width=None):
    """
    Filters by length of approximate width of words rendered

    char_widths is a tuple of format (('a', 300), ('b', 540))

    Example:
    >>> data = (("ba", 1), ("cab", 1), ("cabo", 1))
    >>> widths = (('a', 5), ('b', 10), ('c', 15), ('o', 20))
    >>> width_filter(data, widths)
    (('ba', 1), ('cab', 1), ('cabo', 1))
    >>> width_filter(data, widths, min_width = 30)
    (('cab', 1), ('cabo', 1))
    >>> width_filter(data, widths, max_width = 30)
    (('ba', 1), ('cab', 1))
    >>> width_filter(data, widths, width = 15)
    (('ba', 1),)
    """
    width_dict = dict(char_widths)

    def word_width(word):
        return sum(width_dict[c] for c in word)

    if min_width or max_width < BIG_NUM:
        return tuple(
            (word, count)
            for word, count in words_count
            if min_width <= word_width(word) <= max_width
        )
    elif width:
        return tuple(
            (word, count) for word, count in words_count if width == word_width(word)
        )
    else:
        return words_count
