from functools import lru_cache
from itertools import accumulate
from .punctuation import punctuate
from .sources import BIG_NUM, FilterError
import sys
import random


DEFAULT_MIN_NUM_WORDS = 5
DEFAULT_MAX_NUM_WORDS = 20
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


def gen_numeral(rand, glyphs=None, wl=None, min_wl=1, max_wl=None, raise_errors=False):
    if max_wl is None:
        max_wl = 4

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
            if raise_errors:
                raise FilterError("No numerals available in glyphs")
            else:
                print("Error:", "No numerals available in glyphs", file=sys.stderr)
                return ""

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
        n=None,
        numerals=0,
        seed=None,
        top_k=BIG_NUM,
        case="any",
        min_wl=1,
        max_wl=None,
        wl=None,
        contains=None,
        inner=None,
        startswith=None,
        endswith=None,
        regexp=None,
        raise_errors=False,
    ):
        if seed:
            self.rand.seed(seed)

        try:
            filtered_data = self.wc_source.filter_data(
                glyphs,
                top_k=top_k,
                case=case,
                min_wl=min_wl,
                max_wl=max_wl,
                wl=wl,
                contains=contains,
                inner=inner,
                startswith=startswith,
                endswith=endswith,
                regexp=regexp,
            )
        except FilterError as e:
            if raise_errors:
                raise e
            else:
                print("Error:", e.args[0], file=sys.stderr)
                return ""

        word_temp = temp if word_temp is None else word_temp

        if not (0 <= numerals <= 1):
            raise ValueError("'numerals' must be between 0 and 1")

        if n is None:
            word_type = self.rand.choices(
                ["sample_weighted", "numeral"],
                weights=[1 - numerals, numerals],
            )[0]
            if word_type == "sample_weighted":
                return sample_word_weighted(filtered_data, self.rand, word_temp)
            elif word_type == "numeral":
                return gen_numeral(
                    self.rand,
                    glyphs=glyphs,
                    min_wl=min_wl,
                    max_wl=max_wl,
                    raise_errors=raise_errors,
                )
        else:
            return filtered_data[n][0]

    def words(
        self,
        glyphs=None,
        seed=None,
        seq=False,
        num_words=None,
        min_num_words=DEFAULT_MIN_NUM_WORDS,
        max_num_words=DEFAULT_MAX_NUM_WORDS,
        cap_first=None,
        case="any",
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)

        if not num_words:
            num_words = self.rand.randint(min_num_words, max_num_words)

        if cap_first is None:
            # if there are uppercase letters and cap_first isn't set, default to true
            if glyphs:
                cap_first = bool("".join([c for c in glyphs if c.isupper()]))
            else:
                cap_first = True

        def case_per_word(i):
            # cap_first only applies case='cap' to first word if case is not set
            if cap_first and case == "any" and i == 0:
                return "cap"
            else:
                return case

        if seq:
            word_list = [
                self.word(glyphs=glyphs, case=case_per_word(i), n=i, **kwargs)
                for i in range(num_words)
            ]
        else:
            word_list = [
                self.word(glyphs=glyphs, case=case_per_word(i), **kwargs)
                for i in range(num_words)
            ]

        return [w for w in word_list if w]

    def sent(
        self,
        glyphs=None,
        seed=None,
        punc_temp=None,
        temp=1,
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)

        punc_temp = temp if punc_temp is None else punc_temp

        words = self.words(
            glyphs=glyphs,
            **kwargs,
        )
        return punctuate(self.punctuation, self.rand, words, glyphs, punc_temp)

    def sents(
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

        return [self.sent(**kwargs) for _ in range(para_len)]

    def para(self, seed=None, sent_sep=" ", **kwargs):
        if seed:
            self.rand.seed(seed)

        return sent_sep.join(self.sents(**kwargs))

    def paras(
        self,
        seed=None,
        num_paras=3,
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)
        return [self.para(**kwargs) for _ in range(num_paras)]

    def text(self, seed=None, para_sep="\n\n", **kwargs):
        if seed:
            self.rand.seed(seed)

        return para_sep.join(self.paras(**kwargs))
