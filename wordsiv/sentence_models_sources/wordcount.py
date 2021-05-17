from functools import lru_cache
from collections import OrderedDict
from itertools import islice, cycle
import random
import reprlib
from pathlib import Path
import os
import re
import json

from ..utilities import has_glyphs, Hashabledict, HashabledictKeys
from ..source import BaseSource
from .base_sentence_model import BaseSentenceModel
from ..datawrapper import DataWrapper, unwrap
from ..punctuation import punctuate

BIG_NUM = 100000

DEFAULT_MIN_SENT_LEN = 7
DEFAULT_MAX_SENT_LEN = 20
DEFAULT_SEQ_NUM_WORDS = 10

TEST_MODULES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / "../../tests/test_source_modules"
)

#####################################################################################
###### UTILITY
######################################################################################


@lru_cache(maxsize=None)
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
            TEST_MODULES_DIR / "wctest/data/count-source.txt", {}, lines=3)
    >>> obj.data_wrap.data
    (('gather', 94), ('to', 119), ('sublimedirectory', 204), ('sublimedirectory', 12))
    """

    def __init__(self, data_file, meta, lines=None):
        self.data_file = data_file
        self.lines = lines
        self.meta = meta

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def data_wrap(self):
        """for a WordCountSource, data is a tuple of tuples"""

        return DataWrapper(tuple(stream_file_tuples(self.data_file, self.lines)))


#####################################################################################
###### WORDTEXT MODELS
#####################################################################################


@lru_cache(maxsize=None)
def prob_wordcount_gen(data_wrap, rand):
    word_list, counts = zip_tuple(data_wrap.data)
    while True:
        yield rand.choices(word_list, k=1, weights=counts)[0]


@lru_cache(maxsize=None)
def rand_wordcount_gen(data_wrap, rand):
    word_list, _ = zip_tuple(data_wrap.data)
    while True:
        yield rand.choice(word_list)


class RandomModel(BaseSentenceModel):
    """SentenceModel which randomly selects words"""

    @classmethod
    def create_model(
        cls, data_wrap, available_glyphs, font_info, rand, language, **kwargs
    ):
        """Creates model, returning (model, **kwargs)"""

        model = cls(data_wrap, available_glyphs, font_info, rand, language)
        return model, kwargs

    def __init__(self, data_wrap, available_glyphs, font_info, rand, language):

        # No filtering on initialization since filtering happens at word level
        self.data_wrap = data_wrap
        self.available_glyphs = available_glyphs
        self.font_info = font_info
        self.rand = rand
        self.language = language

    def word(self, prob=True, **kwargs):
        """Return a random word

        Keyword Args:
            prob: favor words with higher wordcounts
            uc (bool): Uppercase word
            lc (bool): Lowercase word
            cap (bool): Capitalize word
            num_top (int): Limit number of words drawn from
            min_wl (int): Minimum word length,
            max_wl (int): Maximum word length,
            wl (int): Word length,
            min_width (int): Minimum approximate rendered word width
            max_width (int): Maximum approximate rendered word width
            width (int): Approximate rendered word width
        """

        filtered_data_wrap = filter_data(
            self.data_wrap, self.available_glyphs, self.font_info, **kwargs
        )
        if prob:
            gen = prob_wordcount_gen(filtered_data_wrap, self.rand)
        else:
            gen = rand_wordcount_gen(filtered_data_wrap, self.rand)

        return next(gen)

    def words(
        self,
        num_words=None,
        min_num_words=DEFAULT_MIN_SENT_LEN,
        max_num_words=DEFAULT_MAX_SENT_LEN,
        cap_first=False,
        uc=False,
        lc=False,
        cap=False,
        **kwargs
    ):
        """Return a list of random words

        Keyword Args:
            min_num_words: Minimum number of words
            max_num_words: Maximum number of words
            num_words: Number of words to generate
            cap_first (bool): Capitalize first word in word list
            prob: favor words with higher wordcounts
            uc (bool): Uppercase all words
            lc (bool): Lowercase all words
            cap (bool): Capitalize all words
            num_top (int): Limit number of words drawn from
            min_wl (int): Minimum word length
            max_wl (int): Maximum word length
            wl (int): Word length
            min_width (int): Minimum approximate rendered word width
            max_width (int): Maximum approximate rendered word width
            width (int): Approximate rendered word width
        """

        if not num_words:
            num_words = self.rand.randint(min_num_words, max_num_words)

        def should_cap_first(n):
            return cap or (cap_first and n == 0)

        return [
            self.word(cap=should_cap_first(n), uc=uc, lc=lc, **kwargs)
            for n in range(num_words)
        ]

    def sentence(
        self,
        cap_sent=True,
        min_sent_len=DEFAULT_MIN_SENT_LEN,
        max_sent_len=DEFAULT_MAX_SENT_LEN,
        sent_len=None,
        punc_func=None,
        **kwargs
    ):
        """Return a random sentence

        Keyword Args:
            min_sent_len: Minimum number of words per sentence
            max_sent_len: Maximum number of words per sentence
            sent_len: Number of words per sentence
            cap_first (bool): Capitalize first word of sentence
            punc_func (function): Function which wraps sentence with punctuation
            prob: favor words with higher wordcounts
            uc (bool): Uppercase all words
            lc (bool): Lowercase all words
            cap (bool): Capitalize all words
            num_top (int): Limit number of words drawn from
            min_wl (int): Minimum word length
            max_wl (int): Maximum word length
            wl (int): Word length
            min_width (int): Minimum approximate rendered word width
            max_width (int): Maximum approximate rendered word width
            width (int): Approximate rendered word width
        """

        words = self.words(
            cap_first=cap_sent,
            min_num_words=min_sent_len,
            max_num_words=max_sent_len,
            num_words=sent_len,
            **kwargs
        )
        return punctuate(
            words,
            self.available_glyphs.glyphs_string,
            self.rand,
            self.language,
            punc_func,
        )


@lru_cache(maxsize=None)
def sequential_gen(data_wrap):
    for word, _ in cycle(data_wrap.data):
        yield word


class SequentialModel(BaseSentenceModel):
    """SentenceModel which returns words sequentially in the order of the source data"""

    @classmethod
    def create_model(
        cls, data_wrap, available_glyphs, font_info, rand, language, **kwargs
    ):
        """Creates model, returning (model, **kwargs)"""

        model = cls(data_wrap, available_glyphs, font_info)
        return model, kwargs

    def __init__(self, data_wrap, available_glyphs, font_info):

        # No filtering on initialization since filtering happens at word level
        self.data_wrap = data_wrap
        self.available_glyphs = available_glyphs
        self.font_info = font_info

    def words(
        self,
        num_words=DEFAULT_SEQ_NUM_WORDS,
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
        """Return a list of sequential words from the source

        Keyword Args:
            num_words: Number of words to generate
            uc (bool): Uppercase all words
            lc (bool): Lowercase all words
            cap (bool): Capitalize all words
            min_wl (int): Minimum word length
            max_wl (int): Maximum word length
            wl (int): Word length
            min_width (int): Minimum approximate rendered word width
            max_width (int): Maximum approximate rendered word width
            width (int): Approximate rendered word width
        """

        filtered_data_wrap = filter_data(
            self.data_wrap,
            self.available_glyphs,
            self.font_info,
            uc=uc,
            lc=lc,
            cap=cap,
            min_wl=min_wl,
            max_wl=max_wl,
            wl=wl,
            min_width=min_width,
            max_width=max_width,
            width=width,
        )

        gen = sequential_gen(filtered_data_wrap)
        return [next(gen) for n in range(num_words)]


#####################################################################################
###### FILTERS
#####################################################################################


@lru_cache(maxsize=None)
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

    glyphs_string = available_glyphs.glyphs_string if available_glyphs.limited else None

    if uc:
        dw = uc_filter(dw, glyphs_string)
    elif lc:
        dw = lc_filter(dw, glyphs_string)
    elif cap:
        dw = cap_filter(dw, glyphs_string)
    else:
        dw = available_filter(dw, glyphs_string)

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
