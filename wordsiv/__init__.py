"""WordSiv is a Python library for generating proofing text with a limited character set."""

from functools import cached_property, lru_cache
from itertools import accumulate
import logging
import random
import regex
import json
from math import exp
from . import vocab_data
from importlib import resources
from .filter import FilterError, BIG_NUM, filter_wordcount

log = logging.getLogger(__name__)

DEFAULT_MIN_NUM_WORDS = 10
DEFAULT_MAX_NUM_WORDS = 20
DEFAULT_TOP_NUM_WORDS = 10
DEFAULT_MIN_PARA_LEN = 4
DEFAULT_MAX_PARA_LEN = 7

DEFAULT_VOCABS = {
    "ar": ("ar_subs_meta.json", "ar_subs.tsv"),
    "en": ("en_books_meta.json", "en_books.tsv"),
    "es": ("es_subs_meta.json", "es_subs.tsv"),
    "fa": ("fa_subs_meta.json", "fa_subs.tsv"),
}

DEFAULT_PUNCTUATION = {
    "en": {
        "start": {"": 1.0},
        "insert": {
            " ": 0.365,
            ", ": 0.403,
            ": ": 0.088,
            "; ": 0.058,
            "–": 0.057,
            "—": 0.022,
            " … ": 0.006,
        },
        "wrap_sent": {
            ("", "."): 0.923,
            ("", "!"): 0.034,
            ("", "?"): 0.04,
            ("", "…"): 0.003,
        },
        "wrap_inner": {
            ("", ""): 0.825,
            ("(", ")"): 0.133,
            ("‘", "’"): 0.013,
            ("“", "”"): 0.028,
        },
    },
    "ar": {
        "insert": {" ": 0.364, ": ": 0.108, "، ": 0.463, "؛ ": 0.066},
        "wrap_sent": {("", "."): 0.914, ("", "؟"): 0.052, ("", "!"): 0.033},
        "wrap_inner": {("", ""): 0.971, ("’", "‘"): 0.007, ("”", "“"): 0.022},
    },
    "fa": {
        "insert": {" ": 0.364, ": ": 0.108, "، ": 0.463, "؛ ": 0.066},
        "wrap_sent": {("", "."): 0.914, ("", "؟"): 0.052, ("", "!"): 0.033},
        "wrap_inner": {("", ""): 0.971, ("’", "‘"): 0.007, ("”", "“"): 0.022},
    },
    "es": {
        "start": {"": 100},
        "insert": {
            " ": 0.277,
            ", ": 0.49,
            ": ": 0.093,
            "; ": 0.073,
            "– ": 0.026,
            "— ": 0.03,
            "… ": 0.011,
        },
        "wrap_sent": {
            ("", "."): 0.928,
            ("¡", "!"): 0.029,
            ("¿", "?"): 0.036,
            ("", "…"): 0.008,
        },
        "wrap_inner": {
            ("", ""): 0.814,
            ("(", ")"): 0.129,
            ("‘", "’"): 0.013,
            ("“", "”"): 0.044,
        },
    },
}


def _punctuate(
    punctuation: dict,
    rand: random.Random,
    words: list[str],
    glyphs: str,
    rnd_punc: float,
):
    """Punctuate a list of words and join into a sentence using a punctuation dict"""

    def random_available(option_weight, glyphs: str, rand, rnd_punc: float):
        punc_prob = {
            (punc, (1 - rnd_punc) * prob + rnd_punc * 1)
            for punc, prob in option_weight.items()
            # if glyphs is set, check if we have the glyphs we need to punctuate
            # we aren't strict about having spaces, hence glyphs + ' '
            if not glyphs or all(c in glyphs + " " for c in punc)
        }

        if punc_prob:
            options, weights = zip(*punc_prob)
            return rand.choices(options, weights=weights, k=1)[0]
        else:
            return None

    insert = random_available(punctuation["insert"], glyphs, rand, rnd_punc) or ""
    wrap_sent = random_available(punctuation["wrap_sent"], glyphs, rand, rnd_punc) or (
        "",
        "",
    )
    wrap_inner = random_available(
        punctuation["wrap_inner"], glyphs, rand, rnd_punc
    ) or ("", "")

    if len(words) > 2:
        tokens = []

        # place inner wrap punctuation on words (parentheses, quotes, etc)
        wrap_left_index = rand.randrange(0, len(words) - 1)
        wrap_right_index = rand.randrange(wrap_left_index, len(words) - 1)
        words[wrap_left_index] = wrap_inner[0] + words[wrap_left_index]
        words[wrap_right_index] = words[wrap_right_index] + wrap_inner[1]

        # add insert punctuation and spaces
        # pick an index that hasn't already been used (simpler)
        insert_index = rand.choice(
            [
                n
                for n in range(1, len(words) - 1)
                if n not in [words[wrap_left_index], words[wrap_right_index]]
            ]
        )

        # put "insert" punctuation in place of a space
        separators = [" "] * (len(words) - 1)
        separators[insert_index - 1] = insert
        sent = "".join(
            [t for pair in zip(words, separators) for t in pair] + [words[-1]]
        )
    else:
        sent = " ".join(words)

    # place surrounding punctuation
    return wrap_sent[0] + sent + wrap_sent[1]


@lru_cache(maxsize=None)
def _accumulate_weights(counts: list[int]) -> list[int]:
    """Accumulate weights and cache results for speed"""

    return list(accumulate(counts))


@lru_cache(maxsize=None)
def _split_wordcount(
    word_count: list[tuple[str, int]]
) -> tuple[tuple[str], tuple[int]]:
    """Split a wordcount list into words and counts."""

    return tuple(i[0] for i in word_count), tuple(i[1] for i in word_count)


@lru_cache(maxsize=None)
def _interpolate_counts(counts: tuple[int], rnd: float) -> tuple[int]:
    """Interpolate counts with random distribution."""

    max_count = max(counts)
    adjusted_counts = tuple((1 - rnd) * c + rnd * max_count for c in counts)
    return adjusted_counts


def _sample_word(
    word_count: list[tuple[str, int]], rand: random.Random, rnd: float
) -> str:
    """Sample a word from a wordcount list."""

    words, counts = _split_wordcount(word_count)
    adjusted_counts = _interpolate_counts(counts, rnd)
    accumulated_counts = _accumulate_weights(adjusted_counts)

    return rand.choices(words, cum_weights=accumulated_counts)[0]


class VocabEmptyError(Exception):
    pass


class VocabFormatError(Exception):
    pass


class Vocab:
    """A vocabulary of words and occurrence counts with metadata for filtering and punctuating.

    Attributes:
        bicameral (bool): Specifies whether the vocabulary has uppercase and lowercase letters.
        data (str): A TSV-formatted string with word, count pairs or a newline-delimited list of words.
        data_file (str): A path to a file to supply the data instead of the data attribute
        punctuation (Punctuation): A Punctuation object for handling punctuation in generated text.
    """

    def __init__(
        self,
        lang: str,
        bicameral: bool,
        punctuation: dict = None,
        data: str = None,
        data_file: str = None,
        meta: dict = None,
    ):
        """Initializes the Vocab instance."""

        self.lang = lang
        self.bicameral = bicameral
        self.punctuation = punctuation
        self._data = data
        self.data_file = data_file
        self.meta = meta

        if data and data_file:
            raise ValueError("Cannot specify both 'data' and 'data_file'")
        elif data is None and not data_file:
            raise ValueError("Must specify either 'data' or 'data_file'")

    @cached_property
    def data(self):
        """Returns raw data from parameter _data or data_file."""

        if self._data is not None:
            data = self._data
        elif getattr(self, "data_file", None):
            with open(self.data_file, "r", encoding="utf8") as f:
                data = f.read()
        if not data:
            raise VocabEmptyError(f"No data found in {self.data_file}")

        return data

    @cached_property
    def wordcount_str(self) -> str:
        """Returns a TSV-formatted string with words and counts."""

        firstline = self.data.partition("\n")[0]

        if regex.match(r"[[:alpha:]]+\t\d+$", firstline):
            # if we have counts, return the original string
            return self.data
        elif regex.match(r"[[:alpha:]]+$", firstline):
            # if we just have newline-delimited words, add counts of 1
            return "\n".join(f"{w}\t1" for w in self.data.splitlines())
        else:
            raise VocabFormatError(
                "The vocab file is formatted incorrectly. "
                "Should be a TSV file with words and counts as columns, or a newline-delimited list of words."
            )

    @cached_property
    def wordcount(self) -> list[tuple[str, int]]:
        """Returns a list of tuples with words and counts."""

        return [
            (l.split()[0], int(l.split()[1])) for l in self.wordcount_str.splitlines()
        ]

    @lru_cache(maxsize=None)
    def filter(self, *args, **kwargs):
        return filter_wordcount(self.wordcount_str, self.bicameral, *args, **kwargs)


class WordSiv:
    """A class that consumes Vocabs to generate text.

    Class Variables:
        default_glyphs (str): The set of glyphs that constrains the words generated.
        default_vocab (str): The name of the default Vocab.
        vocabs (dict): A dictionary of Vocab names and objects.
        rand (Random): An instance of random.Random for generating random numbers.

    Args:
        glyphs (str): The set of glyphs that constrains the words generated.
        vocab (str): The name of the default vocab.
        add_default_vocabs (bool): Whether to add the default vocabs.
    """

    def __init__(
        self,
        glyphs: str = None,
        vocab: str = None,
        add_default_vocabs=True,
        raise_errors=False,
    ):
        self.default_glyphs = glyphs
        self.default_vocab = vocab
        self.raise_errors = raise_errors
        self.vocabs = {}

        if add_default_vocabs:
            self.add_default_vocabs()

        self.rand = random.Random()

    def set_glyphs(self, default_glyphs: str) -> None:
        """Set the default glyph set for the WordSiv instance.

        Args:
            default_glyphs (str): A string of glyphs
        """
        self.default_glyphs = default_glyphs

    def add_vocab(self, vocab_name: str, vocab: Vocab) -> None:
        """Add a Vocab to the WordSiv instance.

        Args:
            vocab_name (str): a name to access the Vocab with
            vocab (Vocab): The Vocab object.
        """
        self.vocabs[vocab_name] = vocab

    def add_default_vocabs(self) -> None:
        for vocab_name, (meta_file, data_file) in DEFAULT_VOCABS.items():

            meta_path = resources.files(vocab_data) / meta_file
            with open(meta_path, "r", encoding="utf8") as f:
                meta = json.load(f)

            data_path = resources.files(vocab_data) / data_file
            vocab = Vocab(
                meta["lang"], meta["bicameral"], meta=meta, data_file=data_path
            )
            self.add_vocab(vocab_name, vocab)

    def set_vocab(self, default_vocab: str) -> None:
        """Set the default vocab for the WordSiv instance.

        Args:
            default_vocab (str): The name of the default vocab.
        """
        self.default_vocab = default_vocab

    def get_vocab(self, vocab_name: str) -> Vocab:
        """Given the name of the vocab, return the Vocab object.

        Args:
            vocab_name (str): The name of the vocab.

        Returns:
            Vocab: The Vocab object.
        """
        return self.vocabs[vocab_name]

    def number(
        self, seed=None, glyphs=None, wl=None, min_wl=1, max_wl=None, raise_errors=False
    ):

        glyphs = self.default_glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors

        if seed:
            self.rand.seed(seed)

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
                    log.warning("No numerals available in glyphs")
                    return ""

        length = random.randint(min_wl, max_wl)
        return "".join(self.rand.choice(available_numerals) for _ in range(length))

    def word(
        self,
        vocab: str = None,
        glyphs: str = None,
        rnd: float = 0,
        seed: int = None,
        case: str = "any",
        top_k: int = BIG_NUM,
        min_wl: int = 1,
        max_wl: int = None,
        wl: int = None,
        contains: str = None,
        inner: str = None,
        startswith: str = None,
        endswith: str = None,
        regexp: str = None,
        raise_errors: bool = False,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors
        vocab = (
            self.get_vocab(self.default_vocab) if not vocab else self.get_vocab(vocab)
        )
        if rnd < 0 or rnd > 1:
            raise ValueError("'rnd' must be between 0 and 1")

        if seed:
            self.rand.seed(seed)

        try:
            wc_list = vocab.filter(
                glyphs,
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
                log.warning("%s", e.args[0])
                return ""

        # limit number of words if top_k is set
        if top_k:
            wc_list = wc_list[:top_k]

        return _sample_word(wc_list, self.rand, rnd)

    def top_word(
        self,
        idx: int = 0,
        vocab: str = None,
        glyphs: str = None,
        case: str = "any",
        min_wl: int = 2,
        max_wl: int = None,
        wl: int = None,
        contains: str = None,
        inner: str = None,
        startswith: str = None,
        endswith: str = None,
        regexp: str = None,
        raise_errors: bool = False,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors
        vocab = (
            self.get_vocab(self.default_vocab) if not vocab else self.get_vocab(vocab)
        )

        try:
            wc_list = vocab.filter(
                glyphs,
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
                log.warning("%s", e.args[0])
                return ""

        try:
            return wc_list[idx][0]
        except IndexError:
            if raise_errors:
                raise FilterError(f"No word at index idx='{idx}'")
            else:
                log.warning("No word at index idx='%s'", idx)
                return ""

    def words(
        self,
        glyphs=None,
        seed=None,
        n_words=None,
        min_n_words=DEFAULT_MIN_NUM_WORDS,
        max_n_words=DEFAULT_MAX_NUM_WORDS,
        numbers=0,
        cap_first=None,
        case="any",
        rnd=0,
        **kwargs,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs

        if seed:
            self.rand.seed(seed)

        if not n_words:
            n_words = self.rand.randint(min_n_words, max_n_words)

        if cap_first is None:
            if glyphs:
                # if we're constrained to glyphs, only capitalize first word if there's an uppercase letter
                cap_first = any(c for c in glyphs if c.isupper())
            else:
                # otherwise, capitalize the first word
                cap_first = True

        if not (0 <= numbers <= 1):
            raise ValueError("'numbers' must be between 0 and 1")

        word_list = []

        last_w = None
        for i in range(n_words):
            if cap_first and case == "any" and i == 0:
                word_case = "cap"
            else:
                word_case = case

            token_type = self.rand.choices(
                ["word", "number"],
                weights=[1 - numbers, numbers],
            )[0]

            if token_type == "word":
                w = self.word(glyphs=glyphs, case=word_case, rnd=rnd, **kwargs)

                # try once to avoid repeat words
                if w == last_w:
                    w = self.word(glyphs=glyphs, case=word_case, rnd=rnd, **kwargs)

                # w can be empty string if no matching word is found and we fail gently
                if w:
                    word_list.append(w)
                    last_w = w
            elif token_type == "number":
                w = self.number(glyphs=glyphs, **kwargs)

                # w can be empty string if no numeral is available with the glyphs we have
                if w:
                    word_list.append(w)
                    last_w = w

        return word_list

    def top_words(
        self,
        n_words: int = DEFAULT_TOP_NUM_WORDS,
        idx: int = 0,
        glyphs=None,
        **kwargs,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs

        word_list = [
            self.top_word(glyphs=glyphs, idx=i, **kwargs)
            for i in range(idx, idx + n_words)
        ]

        # filter out empty words (since by default we fail gently, this is a proof)
        return [w for w in word_list if w]

    def sent(
        self,
        vocab: str = None,
        glyphs=None,
        seed=None,
        punc=True,
        rnd_punc=0,
        **kwargs,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs

        if seed:
            self.rand.seed(seed)

        word_list = self.words(
            glyphs=glyphs,
            **kwargs,
        )

        if punc:
            if rnd_punc < 0 or rnd_punc > 1:
                raise ValueError("'rnd_punc' must be between 0 and 1")

            vocab = (
                self.get_vocab(vocab) if vocab else self.get_vocab(self.default_vocab)
            )

            if vocab.punctuation:
                punctuation = vocab.punctuation
            else:
                try:
                    punctuation = DEFAULT_PUNCTUATION[vocab.lang]
                except KeyError:
                    return " ".join(words)

            return _punctuate(
                punctuation,
                self.rand,
                word_list,
                glyphs,
                rnd_punc,
            )

        else:
            return " ".join(word_list)

    def sents(
        self,
        seed=None,
        min_n_sents=DEFAULT_MIN_PARA_LEN,
        max_n_sents=DEFAULT_MAX_PARA_LEN,
        n_sents=None,
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)

        if not n_sents:
            n_sents = random.randint(min_n_sents, max_n_sents)

        return [self.sent(**kwargs) for _ in range(n_sents)]

    def para(self, seed=None, sent_sep=" ", **kwargs):
        if seed:
            self.rand.seed(seed)

        return sent_sep.join(self.sents(**kwargs))

    def paras(
        self,
        seed=None,
        n_paras=3,
        **kwargs,
    ):
        if seed:
            self.rand.seed(seed)
        return [self.para(**kwargs) for _ in range(n_paras)]

    def text(self, seed=None, para_sep="\n\n", **kwargs):
        if seed:
            self.rand.seed(seed)

        return para_sep.join(self.paras(**kwargs))


_wordsiv_instance = WordSiv()


def set_glyphs(default_glyphs):
    return _wordsiv_instance.set_glyphs(default_glyphs)


def set_vocab(default_vocab):
    return _wordsiv_instance.set_vocab(default_vocab)


def get_vocab(vocab_name):
    return _wordsiv_instance.get_vocab(vocab_name)


def add_vocab(vocab_name, vocab):
    return _wordsiv_instance.add_vocab(vocab_name, vocab)


def number(**kwargs):
    return _wordsiv_instance.number(**kwargs)


def word(**kwargs):
    return _wordsiv_instance.word(**kwargs)


def top_word(*args, **kwargs):
    return _wordsiv_instance.top_word(*args, **kwargs)


def words(**kwargs):
    return _wordsiv_instance.words(**kwargs)


def top_words(*args, **kwargs):
    return _wordsiv_instance.top_words(*args, **kwargs)


def sent(**kwargs):
    return _wordsiv_instance.sent(**kwargs)


def sents(**kwargs):
    return _wordsiv_instance.sents(**kwargs)


def para(**kwargs):
    return _wordsiv_instance.para(**kwargs)


def paras(**kwargs):
    return _wordsiv_instance.paras(**kwargs)


def text(**kwargs):
    return _wordsiv_instance.text(**kwargs)
