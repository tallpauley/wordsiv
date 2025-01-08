"""WordSiv is a Python library for generating proofing text with a limited character set."""

from __future__ import annotations

from functools import lru_cache
from itertools import accumulate
import logging
import random
import json
from importlib import resources
from typing import Sequence
from ._vocab import Vocab, VocabFormatError, VocabEmptyError
from ._filter import FilterError, CaseType
from ._punctuation import DEFAULT_PUNCTUATION, _punctuate
from . import vocab_data

__all__ = [
    "WordSiv",
    "Vocab",
    "FilterError",
    "CaseType",
    "VocabFormatError",
    "VocabEmptyError",
]

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
def _accumulate_weights(counts: tuple[float, ...]) -> tuple[float, ...]:
    """Accumulate weights and cache results"""

    return tuple(accumulate(counts))


@lru_cache(maxsize=None)
def _split_wordcount(
    word_count: tuple[tuple[str, int], ...],
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Split a wordcount list into words and counts and cache results"""

    return tuple(i[0] for i in word_count), tuple(i[1] for i in word_count)


@lru_cache(maxsize=None)
def _interpolate_counts(counts: tuple[float, ...], rnd: float) -> tuple[float, ...]:
    """Interpolate counts with a random distribution."""

    max_count = max(counts)
    adjusted_counts = tuple((1 - rnd) * c + rnd * max_count for c in counts)
    return adjusted_counts


def _sample_word(
    word_count: tuple[tuple[str, float], ...], rand: random.Random, rnd: float
) -> str:
    """Sample a word from a wordcount list."""

    words, counts = _split_wordcount(word_count)
    adjusted_counts = _interpolate_counts(counts, rnd)
    accumulated_counts = _accumulate_weights(adjusted_counts)

    return rand.choices(words, cum_weights=accumulated_counts)[0]


class WordSiv:
    """The main WordSiv object which uses Vocabs to generates text.

    This object is the single API for generating text, in which the top-level
    functions call via the singleton `_default_wordsiv_instance`. An object is used to store
    vocab objects (by default those defined in `DEFAULT_VOCABS`) and to store default
    settings (like `glyphs` and `vocab`).

    Args:
        glyphs (str | None): The set of glyphs that constrains the words generated.
        vocab (str | None): The name of the default Vocab.
        add_default_vocabs (bool): Whether to add the default Vocabs.
        raise_errors (bool): Whether to raise errors or fail gently.

    Attributes:
        default_glyphs (str | None): The set of glyphs that constrains the words generated.
        default_vocab (str | None): The name of the default Vocab.
        raise_errors (bool): Whether to raise errors or fail gently.
        vocabs (dict): A dictionary of Vocab names and objects.
        rand (random.Random): An instance of random.Random for generating random numbers.
    """

    def __init__(
        self,
        vocab: str | None = None,
        glyphs: str | None = None,
        add_default_vocabs: bool = True,
        raise_errors: bool = False,
    ):
        self.default_vocab = vocab
        self.default_glyphs = glyphs
        self.raise_errors = raise_errors
        self._vocabs: dict[str, Vocab] = {}

        if add_default_vocabs:
            self._add_default_vocabs()

        self.rand = random.Random()

    def seed(self, seed) -> None:
        """Seed for the random number generator."""
        self.rand.seed(seed)

    def add_vocab(self, vocab_name: str, vocab: Vocab) -> None:
        """Add a Vocab to the WordSiv instance.

        Args:
            vocab_name (str): a name to access the Vocab with
            vocab (Vocab): The Vocab object.
        """
        self._vocabs[vocab_name] = vocab

    def _add_default_vocabs(self) -> None:
        for vocab_name, (meta_file, data_file) in DEFAULT_VOCABS.items():
            meta_path = resources.files(vocab_data) / meta_file
            with meta_path.open("r", encoding="utf8") as f:
                meta = json.load(f)

            data_path = resources.files(vocab_data) / data_file
            vocab = Vocab(
                meta["lang"], bool(meta["bicameral"]), meta=meta, data_file=data_path
            )
            self.add_vocab(vocab_name, vocab)

    def get_vocab(self, vocab_name: str | None = None) -> Vocab:
        """Return the Vocab object with the given name, or the default vocab if `None`.

        Args:
            vocab_name (str | None): The name of the vocab. If `None`, use the default vocab.

        Returns:
            Vocab: The Vocab object.
        """
        if vocab_name:
            return self._vocabs[vocab_name]
        else:
            if self.default_vocab:
                return self._vocabs[self.default_vocab]
            else:
                raise ValueError("Error: no vocab specified")

    def list_vocabs(self) -> list[str]:
        """List all available vocabs."""

        return list(self._vocabs.keys())

    def number(
        self,
        seed=None,
        glyphs: str | None = None,
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
            # TODO put this magic number in a constant
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

        length = self.rand.randint(min_wl, max_wl)
        return "".join(self.rand.choice(available_numerals) for _ in range(length))

    def word(
        self,
        vocab: str | None = None,
        glyphs: str | None = None,
        rnd: float = 0,
        seed=None,
        case: CaseType = "any",
        top_k: int = 0,
        min_wl: int = 1,
        max_wl: int | None = None,
        wl: int | None = None,
        contains: str | Sequence[str] | None = None,
        inner: str | Sequence[str] | None = None,
        startswith: str | None = None,
        endswith: str | None = None,
        regexp: str | None = None,
        raise_errors: bool = False,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors
        vocab_obj = self.get_vocab(vocab)

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
        vocab: str | None = None,
        glyphs: str | None = None,
        idx: int = 0,
        case: CaseType = "any",
        min_wl: int = 2,
        max_wl: int | None = None,
        wl: int | None = None,
        contains: str | Sequence[str] | None = None,
        inner: str | Sequence[str] | None = None,
        startswith: str | None = None,
        endswith: str | None = None,
        regexp: str | Sequence[str] | None = None,
        raise_errors: bool = False,
    ):
        """Return the most common word, or nth most common word (`idx`).

        Args:
            vocab (str | None): The name of the Vocab to use. If `None`, use the default Vocab.
            glyphs (str | None): A whitelist of glyphs to spell words from. If `None`, use the default glyphs.
            idx (int): Select the nth most common word (where `0` is the most common).
            case (CaseType): The desired case of the word. See [`CaseType`][wordsiv.CaseType] for more details.
        """

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
        vocab: str | None = None,
        glyphs: str | None = None,
        seed=None,
        n_words: int | None = None,
        min_n_words: int = DEFAULT_MIN_NUM_WORDS,
        max_n_words: int = DEFAULT_MAX_NUM_WORDS,
        numbers: float = 0,
        cap_first: bool | None = None,
        case: CaseType = "any",
        rnd: float = 0,
        **word_num_kwargs,
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
                word_case = "cap"  # type: CaseType
            else:
                word_case = case

            token_type = self.rand.choices(
                ["word", "number"],
                weights=[1 - numbers, numbers],
            )[0]

            if token_type == "word":
                w = self.word(
                    vocab=vocab,
                    glyphs=glyphs,
                    case=word_case,
                    rnd=rnd,
                    **word_num_kwargs,
                )

                # try once to avoid repeat words
                if w == last_w:
                    w = self.word(
                        vocab=vocab,
                        glyphs=glyphs,
                        case=word_case,
                        rnd=rnd,
                        **word_num_kwargs,
                    )

                # w can be empty string if no matching word is found and we fail gently
                if w:
                    word_list.append(w)
                    last_w = w
            elif token_type == "number":
                w = self.number(glyphs=glyphs, **word_num_kwargs)

                # w can be empty string if no numeral is available with the glyphs we have
                if w:
                    word_list.append(w)
                    last_w = w

        return word_list

    def top_words(
        self,
        glyphs: str | None = None,
        vocab: str | None = None,
        n_words: int = DEFAULT_TOP_NUM_WORDS,
        idx: int = 0,
        case: CaseType = "any",
        min_wl: int = 2,
        max_wl: int | None = None,
        wl: int | None = None,
        contains: str | Sequence[str] | None = None,
        inner: str | Sequence[str] | None = None,
        startswith: str | None = None,
        endswith: str | None = None,
        regexp: str | None = None,
        raise_errors: bool = False,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs
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
            )[idx : idx + n_words]
        except FilterError as e:
            if raise_errors:
                raise e
            else:
                log.warning("%s", e.args[0])
                return []

        if not wc_list:
            if raise_errors:
                raise FilterError(f"No words found at idx '{idx}'")
            else:
                log.warning(f"No words found at idx '{idx}'")
                return []

        return [w for w, _ in wc_list]

    def sent(
        self,
        vocab: str | None = None,
        glyphs: str | None = None,
        seed=None,
        punc: bool = True,
        rnd_punc: float = 0,
        **words_kwargs,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs
        vocab_obj = self.get_vocab(vocab)

        if seed is not None:
            self.rand.seed(seed)

        word_list = self.words(
            glyphs=glyphs,
            vocab=vocab,
            **words_kwargs,
        )

        if punc:
            if rnd_punc < 0 or rnd_punc > 1:
                raise ValueError("'rnd_punc' must be between 0 and 1")

            if vocab_obj.punctuation:
                punctuation = vocab_obj.punctuation
            else:
                try:
                    punctuation = DEFAULT_PUNCTUATION[vocab_obj.lang]
                except KeyError:
                    return " ".join(word_list)

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
        min_n_sents: int = DEFAULT_MIN_PARA_LEN,
        max_n_sents: int = DEFAULT_MAX_PARA_LEN,
        n_sents: int | None = None,
        **sent_kwargs,
    ):
        if seed is not None:
            self.rand.seed(seed)

        if not n_sents:
            n_sents = self.rand.randint(min_n_sents, max_n_sents)

        return [self.sent(**sent_kwargs) for _ in range(n_sents)]

    def para(self, seed=None, sent_sep: str = " ", **sents_kwargs):
        if seed is not None:
            self.rand.seed(seed)

        return sent_sep.join(self.sents(**sents_kwargs))

    def paras(
        self,
        seed=None,
        n_paras: int = 3,
        **para_kwargs,
    ):
        if seed is not None:
            self.rand.seed(seed)

        return [self.para(**para_kwargs) for _ in range(n_paras)]

    def text(
        self,
        seed=None,
        para_sep: str = "\n\n",
        **paras_kwargs,
    ):
        """Generate multiple paragraphs joined by `para_sep`"""

        if seed is not None:
            self.rand.seed(seed)

        return para_sep.join(self.paras(**paras_kwargs))
