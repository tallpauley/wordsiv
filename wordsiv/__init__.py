"""WordSiv is a Python library for generating proofing text with a limited character set."""

from functools import lru_cache
from itertools import accumulate
import logging
import random
import json
from typing import Union
from importlib import resources

from .vocab import Vocab
from .filter import FilterError, BIG_NUM
from .punctuation import DEFAULT_PUNCTUATION, punctuate
from . import vocab_data

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


@lru_cache(maxsize=None)
def _accumulate_weights(counts: tuple[int, ...]) -> tuple[int, ...]:
    """Accumulate weights and cache results"""

    return tuple(accumulate(counts))


@lru_cache(maxsize=None)
def _split_wordcount(
    word_count: tuple[tuple[str, int], ...],
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Split a wordcount list into words and counts and cache results"""

    return tuple(i[0] for i in word_count), tuple(i[1] for i in word_count)


@lru_cache(maxsize=None)
def _interpolate_counts(counts: tuple[int, ...], rnd: float) -> tuple[int, ...]:
    """Interpolate counts with a random distribution."""

    max_count = max(counts)
    adjusted_counts = tuple((1 - rnd) * c + rnd * max_count for c in counts)
    return adjusted_counts


def _sample_word(
    word_count: tuple[tuple[str, int], ...], rand: random.Random, rnd: float
) -> str:
    """Sample a word from a wordcount list."""

    words, counts = _split_wordcount(word_count)
    adjusted_counts = _interpolate_counts(counts, rnd)
    accumulated_counts = _accumulate_weights(adjusted_counts)

    return rand.choices(words, cum_weights=accumulated_counts)[0]


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
        glyphs: Union[str, None] = None,
        vocab: Union[str, None] = None,
        add_default_vocabs: bool = True,
        raise_errors: bool = False,
    ):
        self.default_glyphs = glyphs
        self.default_vocab = vocab
        self.raise_errors = raise_errors
        self.vocabs = {}

        if add_default_vocabs:
            self._add_default_vocabs()

        self.rand = random.Random()

    def set_glyphs(self, default_glyphs: Union[str, None]) -> None:
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

    def _add_default_vocabs(self) -> None:
        for vocab_name, (meta_file, data_file) in DEFAULT_VOCABS.items():
            meta_path = resources.files(vocab_data) / meta_file
            with open(meta_path, "r", encoding="utf8") as f:
                meta = json.load(f)

            data_path = resources.files(vocab_data) / data_file
            vocab = Vocab(
                meta["lang"], bool(meta["bicameral"]), meta=meta, data_file=data_path
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
        self,
        seed=None,
        glyphs: Union[str, None] = None,
        wl=None,
        min_wl=1,
        max_wl=None,
        raise_errors=False,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors

        if seed is not None:
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
        vocab: Union[str, None] = None,
        glyphs: Union[str, None] = None,
        rnd: float = 0,
        seed: Union[None, int, float, str] = None,
        case: str = "any",
        top_k: int = BIG_NUM,
        min_wl: int = 1,
        max_wl: Union[int, None] = None,
        wl: Union[int, None] = None,
        contains: Union[str, None] = None,
        inner: Union[str, None] = None,
        startswith: Union[str, None] = None,
        endswith: Union[str, None] = None,
        regexp: Union[str, None] = None,
        raise_errors: bool = False,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors
        vocab_obj = (
            self.get_vocab(self.default_vocab) if not vocab else self.get_vocab(vocab)
        )
        if rnd < 0 or rnd > 1:
            raise ValueError("'rnd' must be between 0 and 1")

        if seed is not None:
            self.rand.seed(seed)

        try:
            wc_list = vocab_obj.filter(
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
        vocab: Union[str, None] = None,
        glyphs: Union[str, None] = None,
        case: str = "any",
        min_wl: int = 2,
        max_wl: Union[int, None] = None,
        wl: Union[int, None] = None,
        contains: Union[str, None] = None,
        inner: Union[str, None] = None,
        startswith: Union[str, None] = None,
        endswith: Union[str, None] = None,
        regexp: Union[str, None] = None,
        raise_errors: bool = False,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors
        vocab_obj = (
            self.get_vocab(self.default_vocab) if not vocab else self.get_vocab(vocab)
        )

        try:
            wc_list = vocab_obj.filter(
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
        glyphs: Union[str, None] = None,
        seed: Union[None, int, float, str] = None,
        n_words: Union[None, int] = None,
        min_n_words: int = DEFAULT_MIN_NUM_WORDS,
        max_n_words: int = DEFAULT_MAX_NUM_WORDS,
        numbers: float = 0,
        cap_first: Union[None, bool] = None,
        case: str = "any",
        rnd: float = 0,
        **kwargs,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs

        if seed is not None:
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
        glyphs: Union[str, None] = None,
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
        vocab: Union[str, None] = None,
        glyphs: Union[str, None] = None,
        seed: Union[None, int, float, str] = None,
        punc: bool = True,
        rnd_punc: float = 0,
        **kwargs,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs

        if seed is not None:
            self.rand.seed(seed)

        word_list = self.words(
            glyphs=glyphs,
            **kwargs,
        )

        if punc:
            if rnd_punc < 0 or rnd_punc > 1:
                raise ValueError("'rnd_punc' must be between 0 and 1")

            vocab_obj = (
                self.get_vocab(vocab) if vocab else self.get_vocab(self.default_vocab)
            )

            if vocab_obj.punctuation:
                punctuation = vocab_obj.punctuation
            else:
                try:
                    punctuation = DEFAULT_PUNCTUATION[vocab_obj.lang]
                except KeyError:
                    return " ".join(words)

            return punctuate(
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
        seed: Union[None, int, float, str] = None,
        min_n_sents: int = DEFAULT_MIN_PARA_LEN,
        max_n_sents: int = DEFAULT_MAX_PARA_LEN,
        n_sents: Union[None, int] = None,
        **kwargs,
    ):
        if seed is not None:
            self.rand.seed(seed)

        if not n_sents:
            n_sents = random.randint(min_n_sents, max_n_sents)

        return [self.sent(**kwargs) for _ in range(n_sents)]

    def para(self, seed=None, sent_sep: str = " ", **kwargs):
        if seed is not None:
            self.rand.seed(seed)

        return sent_sep.join(self.sents(**kwargs))

    def paras(
        self,
        seed=None,
        n_paras=3,
        **kwargs,
    ):
        if seed is not None:
            self.rand.seed(seed)
        return [self.para(**kwargs) for _ in range(n_paras)]

    def text(
        self, seed=None, para_sep="\n\n", glyphs: Union[str, None] = None, **kwargs
    ):
        if seed is not None:
            self.rand.seed(seed)

        return para_sep.join(self.paras(**kwargs))


_wordsiv_instance = WordSiv()


def set_glyphs(default_glyphs):
    return _wordsiv_instance.set_glyphs(default_glyphs)


def set_vocab(default_vocab: str) -> None:
    return _wordsiv_instance.set_vocab(default_vocab)


def get_vocab(vocab_name: str) -> Vocab:
    return _wordsiv_instance.get_vocab(vocab_name)


def add_vocab(vocab_name: str, vocab: Vocab) -> None:
    return _wordsiv_instance.add_vocab(vocab_name, vocab)


def number(**kwargs) -> str:
    return _wordsiv_instance.number(**kwargs)


def word(**kwargs) -> str:
    return _wordsiv_instance.word(**kwargs)


def top_word(*args, **kwargs) -> str:
    return _wordsiv_instance.top_word(*args, **kwargs)


def words(**kwargs) -> list[str]:
    return _wordsiv_instance.words(**kwargs)


def top_words(**kwargs) -> list[str]:
    return _wordsiv_instance.top_words(**kwargs)


def sent(**kwargs) -> str:
    return _wordsiv_instance.sent(**kwargs)


def sents(**kwargs) -> list[str]:
    return _wordsiv_instance.sents(**kwargs)


def para(**kwargs) -> str:
    return _wordsiv_instance.para(**kwargs)


def paras(**kwargs) -> list[str]:
    return _wordsiv_instance.paras(**kwargs)


def text(**kwargs) -> str:
    return _wordsiv_instance.text(**kwargs)
