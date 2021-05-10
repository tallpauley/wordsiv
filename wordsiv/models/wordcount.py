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
from .source import Source
from .model import Model

BIG_NUM = 100000

TEST_DATA_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__))) / ".." / ".." / "tests" / "data"
)

#####################################################################################
###### SOURCE
######################################################################################


def stream_file_tuples(file, lines=None):
    with open(file, "r") as f:
        lc = 0
        for line in f:
            word, count = re.split("\s+", line.strip())
            yield (word, int(count))

            if lines:
                if lc >= lines:
                    break

                lc += 1


class WordCountSource(Source):
    """A Source that expects a txt file with words and counts

    file looks like this: "koala 235\ncobra 123\n"

    >>> obj = WordCountSource(TEST_DATA_DIR / "count-source.txt")
    >>> obj.data
    (('koala', 2345), ('bear', 1234), ('team', 234), ('collage', 12))
    >>> obj['koala']
    2345
    """

    def __init__(self, data_file, lines=None):
        self.data_file = data_file
        self.lines = lines

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def data(self):
        """for a WordCountSource, data is a tuple of tuples"""

        return tuple(stream_file_tuples(self.data_file, self.lines))

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def as_dict(self):
        return {k: v for (k, v) in self.data}

    def __getitem__(self, key):
        return self.as_dict[key]


#####################################################################################
###### MODELS
#####################################################################################


class WordCountModel(Model):
    @classmethod
    def filtered_model(cls, data, available_glyphs, font_info, rand, **kwargs):
        data = filter_data(data, available_glyphs, font_info, **kwargs)
        return cls(data, available_glyphs, rand=rand)


class ProbabilityModel(WordCountModel):
    """
    A model that uses occurences counts to generate words
    """

    def __init__(self, words_count, available_glyphs, rand):
        self.words_count = words_count
        self.rand = rand
        self.available_glyphs = available_glyphs

        self.words_list, self.counts_list = zip(*self.words_count)

    def word(self, **kwargs):
        return self.rand.choices(self.words_list, k=1, weights=self.counts_list)[0]


class TopModel(WordCountModel):
    """
    A model that spits out the most common words sequentially

    Useful for things like trigrams, where you often just
    want to print out the top few
    """

    def __init__(self, words_count, available_glyphs, rand):
        self.words_count = words_count
        self.rand = rand
        self.available_glyphs = available_glyphs

        self.words_list, _ = zip(*self.words_count)
        self.reset()

    def reset(self):
        self.iterator = self.new_iterator()

    def new_iterator(self):
        return iter(self.words_list)

    def word(self, **kwargs):
        return next(self.iterator)


class RandomModel(WordCountModel):
    """
    A model which picks words completely randomly
    """

    def __init__(self, words_count, available_glyphs, rand):
        self.words_count = words_count
        self.rand = rand
        self.available_glyphs = available_glyphs

        self.words_list, _ = zip(*self.words_count)

    def word(self, **kwargs):
        return self.rand.choice(self.words_list)


#####################################################################################
###### FILTERS
#####################################################################################


def filter_data(
    words_count,
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
    **kwargs
):

    data = words_count

    glyphs_tuple = available_glyphs.glyphs_tuple if available_glyphs.limited else None

    if uc:
        data = uc_filter(data, glyphs_tuple)
    elif lc:
        data = lc_filter(data, glyphs_tuple)
    elif cap:
        data = cap_filter(data, glyphs_tuple)
    else:
        data = available_filter(data, glyphs_tuple)

    if min_wl or max_wl != BIG_NUM or wl:
        data = length_filter(data, min_wl, max_wl, wl)

    if font_info:
        if min_width or max_width != BIG_NUM or width:
            data = width_filter(
                data, font_info.char_widths_tuple(), min_width, max_width, width
            )

    if num_top:
        data = top_filter(words_count, num_top)

    return data


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


@lru_cache(maxsize=None)
def length_filter(words_count, min_wl=0, max_wl=BIG_NUM, wl=None):
    """
    Filters by number of characters in words

    Example:
    """

    if min_wl or max_wl < BIG_NUM:
        return tuple(
            (word, count)
            for word, count in words_count
            if min_wl <= len(word) <= max_wl
        )
    elif wl:
        return tuple((word, count) for word, count in words_count if wl == len(word))
    else:
        return words_count


# Filter by approximate width of text rendered with a font
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
