from functools import lru_cache
from itertools import accumulate
from .punctuation import punctuate
from .sources import BIG_NUM, FilterError
import random


DEFAULT_MIN_SENT_LEN = 5
DEFAULT_MAX_SENT_LEN = 20
DEFAULT_SEQ_NUM_WORDS = 10
DEFAULT_MIN_PARA_LEN = 4
DEFAULT_MAX_PARA_LEN = 7


@lru_cache(maxsize=None)
def accumulate_weights(a_tuple):
    return [i[0] for i in a_tuple], list(accumulate(i[1] for i in a_tuple))


def sample_word_weighted(word_count, rand, temp):
    words, counts = accumulate_weights(word_count)
    adjusted_counts = [count ** (1 / temp) for count in counts]
    return rand.choices(words, cum_weights=adjusted_counts)[0]


def gen_numeral(rand, glyphs=None, wl=None, min_wl=1, max_wl=4, seed=None):

    if wl:
        min_wl = wl
        max_wl = wl
    else:
        if min_wl > max_wl:
            raise ValueError("'min_wl' must be less than or equal to 'max_wl'")

    available_numerals = "".join(str(n) for n in range(0, 10))
    if glyphs:
        available_numerals = "".join(n for n in available_numerals if n in glyphs)

        if not available_numerals:
            raise FilterError("No numerals available in glyphs")

    length = random.randint(min_wl, max_wl)
    return "".join(rand.choice(available_numerals) for _ in range(length))


class WordProbModel:
    def __init__(self, wc_source, punctuation):
        self.wc_source = wc_source
        self.punctuation = punctuation
        self.rand = random.Random()

    def word(
        self,
        glyphs=None,
        temp=1.0,
        word_temp=None,
        punc_temp=None,
        num_prob=0,
        seed=None,
        num_top=BIG_NUM,
        case=None,
        min_wl=0,
        max_wl=BIG_NUM,
        wl=None,
        contains=None,
        startswith=None,
        endswith=None,
        regexp=None,
        respect_case=False,
    ):
        if seed:
            self.rand.seed(seed)

        filtered_data = self.wc_source.filter_data(
            glyphs,
            num_top=num_top,
            case=case,
            min_wl=min_wl,
            max_wl=max_wl,
            wl=wl,
            contains=contains,
            startswith=startswith,
            endswith=endswith,
            regexp=regexp,
            respect_case=respect_case,
        )

        word_temp = temp if word_temp is None else word_temp

        if not (0 <= num_prob <= 1):
            raise ValueError("'num_prob' must be between 0 and 1")

        word_type = self.rand.choices(
            ["sample_weighted", "numeral"],
            weights=[1 - num_prob, num_prob],
        )[0]

        if word_type == "sample_weighted":
            return sample_word_weighted(filtered_data, self.rand, word_temp)
        elif word_type == "numeral":
            return gen_numeral(self.rand, glyphs=glyphs, min_wl=min_wl, max_wl=max_wl)

    def words(
        self,
        seed=None,
        num_words=None,
        min_num_words=DEFAULT_MIN_SENT_LEN,
        max_num_words=DEFAULT_MAX_SENT_LEN,
        cap_first=False,
        case=None,
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)

        if not num_words:
            num_words = self.rand.randint(min_num_words, max_num_words)

        def case_per_word(n):
            if not case and cap_first and n == 0:
                return "cap"
            else:
                return case

        return [self.word(case=case_per_word(n), **kwargs) for n in range(num_words)]

    def sentence(
        self,
        glyphs=None,
        seed=None,
        cap_sent=None,
        min_sent_len=DEFAULT_MIN_SENT_LEN,
        max_sent_len=DEFAULT_MAX_SENT_LEN,
        sent_len=None,
        punc_temp=None,
        temp=1,
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)

        punc_temp = temp if punc_temp is None else punc_temp

        if cap_sent is None:
            # if there are uppercase letters and cap_sent isn't set, default to true
            if glyphs:
                cap_sent = bool("".join([c for c in glyphs if c.isupper()]))
            else:
                cap_sent = True

        words = self.words(
            glyphs=glyphs,
            cap_first=cap_sent,
            min_num_words=min_sent_len,
            max_num_words=max_sent_len,
            num_words=sent_len,
            **kwargs,
        )
        return punctuate(self.punctuation, self.rand, words, glyphs, punc_temp)

    def sentences(
        self,
        seed=None,
        min_para_len=DEFAULT_MIN_PARA_LEN,
        max_para_len=DEFAULT_MAX_PARA_LEN,
        para_len=None,
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)

        if not para_len:
            para_len = random.randint(min_para_len, max_para_len)

        return [self.sentence(**kwargs) for _ in range(para_len)]

    def paragraph(self, seed=None, sent_sep=" ", **kwargs):
        if seed:
            self.rand.seed(seed)

        return sent_sep.join(self.sentences(**kwargs))

    def paragraphs(
        self,
        seed=None,
        num_paras=3,
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)
        return [self.paragraph(**kwargs) for _ in range(num_paras)]

    def text(self, seed=None, para_sep="\n\n", **kwargs):
        if seed:
            self.rand.seed(seed)

        return para_sep.join(self.paragraphs(**kwargs))
