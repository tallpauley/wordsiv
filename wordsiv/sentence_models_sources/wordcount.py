from functools import lru_cache
from itertools import islice, cycle, accumulate
from pathlib import Path
import itertools
import os
import io
import regex
import time

from ..source import BaseSource
from .base_sentence_model import BaseSentenceModel
from ..punctuation import punctuate

BIG_NUM = 2 ** 10

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
def accumulate_weights(a_tuple):
    return [i[0] for i in a_tuple], list(accumulate(i[1] for i in a_tuple))


#####################################################################################
###### SOURCE
######################################################################################


class WordCountSource(BaseSource):
    """A Source that expects a txt file with words and counts

    file looks like this: "koala 235\ncobra 123\n"

    """

    def __init__(self, data_file, meta, lines=None):
        self.data_file = data_file
        self.lines = lines
        self.meta = meta

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def data(self):
        """for a WordCountSource, data is a tuple of tuples"""

        rows = []
        with io.open(self.data_file, "r", encoding="utf8") as f:
            for i, l in enumerate(f):
                rows.append(l)
                if i == self.lines:
                    break
        output = "".join(rows).strip()
        return output


#
#####################################################################################
###### WORDTEXT MODELS
#####################################################################################


def sample_word_weighted(data, rand):
    word_list, counts = accumulate_weights(data)
    return rand.choices(word_list, cum_weights=counts)[0]


def sample_word(word_list, rand):
    return rand.choice([word_list[0] for w in word_list])[0]


class RandomModel(BaseSentenceModel):
    """SentenceModel which randomly selects words"""

    @classmethod
    def create_model(cls, data, available_glyphs, rand, language, **kwargs):
        """Creates model, returning (model, **kwargs)"""

        model = cls(data, available_glyphs, rand, language)
        return model, kwargs

    def __init__(self, data, available_glyphs, rand, language):

        # No filtering on initialization since filtering happens at word level
        self.data = data
        self.available_glyphs = available_glyphs
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
        """

        filtered_data = filter_data(self.data, self.available_glyphs, **kwargs)

        return (
            sample_word_weighted(filtered_data, self.rand)
            if prob
            else sample_word(filtered_data, self.rand)
        )

    def words(
        self,
        num_words=None,
        min_num_words=DEFAULT_MIN_SENT_LEN,
        max_num_words=DEFAULT_MAX_SENT_LEN,
        cap_first=False,
        uc=False,
        lc=False,
        cap=False,
        **kwargs,
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
        **kwargs,
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
        """

        words = self.words(
            cap_first=cap_sent,
            min_num_words=min_sent_len,
            max_num_words=max_sent_len,
            num_words=sent_len,
            **kwargs,
        )
        return punctuate(
            words,
            self.available_glyphs,
            self.rand,
            self.language,
            punc_func,
        )


def sequential_gen(data):
    for word, _ in cycle(data):
        yield word


class SequentialModel(BaseSentenceModel):
    """SentenceModel which returns words sequentially in the order of the source data"""

    @classmethod
    def create_model(cls, data, available_glyphs, rand, language, **kwargs):
        """Creates model, returning (model, **kwargs)"""

        model = cls(data, available_glyphs)
        return model, kwargs

    def __init__(self, data, available_glyphs):

        # No filtering on initialization since filtering happens at word level
        self.data = data
        self.available_glyphs = available_glyphs

    def words(
        self,
        num_words=DEFAULT_SEQ_NUM_WORDS,
        uc=False,
        lc=False,
        cap=False,
        min_wl=0,
        max_wl=BIG_NUM,
        wl=None,
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
        """

        filtered_data = filter_data(
            self.data,
            self.available_glyphs,
            uc=uc,
            lc=lc,
            cap=cap,
            min_wl=min_wl,
            max_wl=max_wl,
            wl=wl,
        )

        gen = sequential_gen(filtered_data)
        return [next(gen) for n in range(num_words)]

    def sentence(self, sent_len=DEFAULT_SEQ_NUM_WORDS, **kwargs):
        """Return a sentence sequential words from the source

        Keyword Args:
            sent_len: Number of words in sentence
            uc (bool): Uppercase all words
            lc (bool): Lowercase all words
            cap (bool): Capitalize all words
            min_wl (int): Minimum word length
            max_wl (int): Maximum word length
            wl (int): Word length
        """

        words = self.words(num_words=sent_len, **kwargs)
        return " ".join(words)


#####################################################################################
###### FILTERS
#####################################################################################


@lru_cache(maxsize=None)
def filter_data(
    wc_str,
    available_glyphs,
    num_top=BIG_NUM,
    uc=False,
    lc=False,
    cap=False,
    min_wl=0,
    max_wl=BIG_NUM,
    wl=None,
    contains=None,
    startswith=None,
    endswith=None,
    regexp=None,
):

    if available_glyphs:
        limited_glyphs = True
        lc_glyphs = "".join([c for c in available_glyphs if c.islower()])
        uc_glyphs = "".join([c for c in available_glyphs if c.isupper()])
    else:
        limited_glyphs = False
        lc_glyphs = None
        uc_glyphs = None

    if uc:
        wc_list = uc_filter(wc_str, uc_glyphs, limited_glyphs)
    elif lc:
        wc_list = lc_filter(wc_str, lc_glyphs, limited_glyphs)
    elif cap:
        wc_list = cap_filter(wc_str, lc_glyphs, uc_glyphs, limited_glyphs)
    else:
        wc_list = available_filter(wc_str, available_glyphs, limited_glyphs)

    # filter by word length
    if min_wl or max_wl != BIG_NUM or wl:
        if wl:
            min_wl = wl
            max_wl = wl

        wc_list = [(w,c) for w,c in wc_list if min_wl <= len(w) <= max_wl]

    # filter by either regex or contains, startswith, endswith
    if regexp:
        if contains or startswith or endswith:
            raise ValueError("Cannot use regexp with contains, startswith or endswith.")

        wc_list = regex_filter(wc_list, regexp)
    else:
        if contains:
            if type(contains) is str:
                contains = [contains]

            for contains_search in contains:
                wc_list = [(w,c) for w,c in wc_list if contains_search in w]


        if startswith:
            wc_list = [(w,c) for w,c in wc_list if w.startswith(startswith)]

        if endswith:
            wc_list = [(w,c) for w,c in wc_list if w.endswith(endswith)]

    # limit number of words if num_top is set
    if num_top:
       wc_list = list(islice(wc_list, num_top))

    if not wc_list:
        raise ValueError("No words available with specified parameters")

    return tuple(wc_list)


def available_filter(
    wc_list: str, available_glyphs_string: str, limited_glyphs: bool
) -> list:
    """
    simply filters out words that have characters not in available_glyphs_string
    keeps casing same as the wordlist
    wc_list is in format (("word", 123), ("word2", 34))
    """

    if limited_glyphs:
        pattern = regex.compile(fr"^[{available_glyphs_string}]+\s+.*", regex.MULTILINE)
        lines = regex.findall(pattern, wc_list)

        # no change of case, leave as appears in wordlist
        return [(l.split()[0], int(l.split()[1])) for l in lines]
    else:
        # simply convert input to list of lists tuples if we're not filtering
        return [(l.split()[0], int(l.split()[1])) for l in wc_list.split("\n")]


def lc_filter(wc_list: str, lc_glyphs: str, limited_glyphs: bool) -> list:
    """
    finds only words that can be spelled with lowercase glyphs
    """

    if limited_glyphs:
        # we only want to look for words that can be spelled with lc_glyphs
        # we wouldn't want to include Berlin (proper), or SMTP (acronym) if we want lowercase
        # if we haven't restricted available glyphs, lc_glyphs will be all unicode
        pattern = regex.compile(fr"^[{lc_glyphs}]+\s+.*", regex.MULTILINE)
        lines = regex.findall(pattern, wc_list)

        # no need to lowercase, we only searched for lowercase words
        return [(l.split()[0], int(l.split()[1])) for l in lines]
    else:
        # if we have all glyphs, simply find lowercase words
        pattern = regex.compile(r"^\p{Ll}+\s+.*", regex.MULTILINE)
        lines = regex.findall(pattern, wc_list)
        return [(l.split()[0], int(l.split()[1])) for l in lines]


def uc_filter(wc_list: str, uc_glyphs: str, limited_glyphs: bool) -> list:
    """
    finds words from wordlist that can be spelled with uc_glyphs AND
    words in wordlist that can be made uppercase and spelled with uc_glyphs
    """

    if limited_glyphs:
        # if our uc_glyphs is 'HAM', we need to also search for 'ham'
        uc_glyphs_lowered = uc_glyphs.lower()

        pattern = regex.compile(fr"^[{uc_glyphs}{uc_glyphs_lowered}]+\s+.*")
        lines = regex.findall(pattern, wc_list)

        # force uppercase on all words
        return [(l.split()[0].upper(), int(l.split()[1])) for l in lines]
    else:
        # no filtering w/ unicode needed if we're uppercasing
        # any word can be made all uppercase
        return [
            (l.split()[0].upper(), int(l.split()[1])) for l in wc_list.split("\n")
        ]


def cap_filter(
    wc_list: str, lc_glyphs: str, uc_glyphs: str, limited_glyphs: bool
) -> list:
    """
    finds capitalized words in the wordlist, and words in the wordlist that can be
    capitalized
    """

    if limited_glyphs:
        # if our available_glyphs is 'Bar', we also need to search for 'bar'
        uc_glyphs_lowered = uc_glyphs.lower()

        # uc_glyphs_lowered is only searched for in the first letter, because word is capitalized
        pattern = regex.compile(
            fr"^[{uc_glyphs}{uc_glyphs_lowered}][{lc_glyphs}]*\s+.*", regex.MULTILINE
        )
        lines = regex.findall(pattern, wc_list)

        # force capitalization
        return [(l.split()[0].capitalize(), int(l.split()[1])) for l in lines]
    else:
        # if we're not restricting glyph set, find words that all BUT first letter are lc
        # Basically just DON'T include acronyms like SMTP (or DDoS!)
        pattern = regex.compile(r"^.\p{Ll}*\s+.*", regex.MULTILINE)
        lines = regex.findall(pattern, wc_list)

        # force capitalization
        return [(l.split()[0].capitalize(), int(l.split()[1])) for l in lines]

def regex_filter(wc_list, regexp):
    pattern = regex.compile(r"^" + regexp + r"\s+.*", regex.MULTILINE)
    wc_str = '\n'.join(f"{w}\t{c}" for w, c in wc_list)
    print(wc_str[0:100])
    lines = regex.findall(pattern, wc_str)

    return [(l.split()[0], int(l.split()[1])) for l in lines]
