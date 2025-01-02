"""WordSiv is a Python library for generating proofing text with a limited character set."""

from __future__ import annotations

from functools import lru_cache
from itertools import accumulate
import logging
import random
import json
from importlib import resources

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
    "word",
    "number",
    "top_word",
    "words",
    "top_words",
    "sent",
    "sents",
    "para",
    "paras",
    "txt",
    "set_glyphs",
    "set_vocab",
    "get_vocab",
    "add_vocab",
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
def _interpolate_counts(counts: tuple[int, ...], rnd: float) -> tuple[int | float, ...]:
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
        glyphs: str | None = None,
        vocab: str | None = None,
        add_default_vocabs: bool = True,
        raise_errors: bool = False,
    ):
        self.default_glyphs = glyphs
        self.default_vocab = vocab
        self.raise_errors = raise_errors
        self.vocabs: dict[str, Vocab] = {}

        if add_default_vocabs:
            self._add_default_vocabs()

        self.rand = random.Random()

    def set_glyphs(self, default_glyphs: str | None) -> None:
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
            with meta_path.open("r", encoding="utf8") as f:
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

    def get_vocab(self, vocab_name: str | None = None) -> Vocab:
        """Return the Vocab object with the given name, or the default vocab if `None`.

        Args:
            vocab_name (str | None): The name of the vocab. If `None`, use the default vocab.

        Returns:
            Vocab: The Vocab object.
        """
        if vocab_name:
            return self.vocabs[vocab_name]
        else:
            if self.default_vocab:
                return self.vocabs[self.default_vocab]
            else:
                raise ValueError("Error: no vocab specified")

    def list_vocabs(self) -> list[str]:
        """List all available vocabs."""

        return list(self.vocabs.keys())

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
        vocab: str | None = None,
        glyphs: str | None = None,
        rnd: float = 0,
        seed: None | int | float | str = None,
        case: CaseType = "any",
        top_k: int = 0,
        min_wl: int = 1,
        max_wl: int | None = None,
        wl: int | None = None,
        contains: str | None = None,
        inner: str | None = None,
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
        contains: str | None = None,
        inner: str | None = None,
        startswith: str | None = None,
        endswith: str | None = None,
        regexp: str | None = None,
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
        glyphs: str | None = None,
        seed: None | int | float | str = None,
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
                w = self.word(glyphs=glyphs, case=word_case, rnd=rnd, **word_num_kwargs)

                # try once to avoid repeat words
                if w == last_w:
                    w = self.word(
                        glyphs=glyphs, case=word_case, rnd=rnd, **word_num_kwargs
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
        n_words: int = DEFAULT_TOP_NUM_WORDS,
        idx: int = 0,
        glyphs: str | None = None,
        **top_word_kwargs,
    ):
        glyphs = self.default_glyphs if not glyphs else glyphs

        word_list = [
            self.top_word(glyphs=glyphs, idx=i, **top_word_kwargs)
            for i in range(idx, idx + n_words)
        ]

        # filter out empty words (since by default we fail gently, this is a proof)
        return [w for w in word_list if w]

    def sent(
        self,
        vocab: str | None = None,
        glyphs: str | None = None,
        seed: None | int | float | str = None,
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
        seed: None | int | float | str = None,
        min_n_sents: int = DEFAULT_MIN_PARA_LEN,
        max_n_sents: int = DEFAULT_MAX_PARA_LEN,
        n_sents: int | None = None,
        **sent_kwargs,
    ):
        if seed is not None:
            self.rand.seed(seed)

        if not n_sents:
            n_sents = random.randint(min_n_sents, max_n_sents)

        return [self.sent(**sent_kwargs) for _ in range(n_sents)]

    def para(self, seed=None, sent_sep: str = " ", **sents_kwargs):
        if seed is not None:
            self.rand.seed(seed)

        return sent_sep.join(self.sents(**sents_kwargs))

    def paras(
        self,
        seed: int | None = None,
        n_paras: int = 3,
        **para_kwargs,
    ):
        if seed is not None:
            self.rand.seed(seed)

        return [self.para(**para_kwargs) for _ in range(n_paras)]

    def txt(
        self,
        seed: None | int | float | str = None,
        para_sep: str = "\n\n",
        **paras_kwargs,
    ):
        """Generate multiple paragraphs joined by `para_sep`"""

        if seed is not None:
            self.rand.seed(seed)

        return para_sep.join(self.paras(**paras_kwargs))


# Top-level convenience functions and singleton WordSiv instance

_default_wordsiv_instance = WordSiv()


def set_glyphs(default_glyphs):
    """Calls [`set_glyphs`][wordsiv.WordSiv.set_glyphs] on default WordSiv instance."""

    return _default_wordsiv_instance.set_glyphs(default_glyphs)


def set_vocab(default_vocab: str) -> None:
    """Calls [`set_vocab`][wordsiv.WordSiv.set_vocab] on default WordSiv instance."""

    return _default_wordsiv_instance.set_vocab(default_vocab)


def get_vocab(vocab_name: str | None) -> Vocab:
    """Calls [`get_vocab`][wordsiv.WordSiv.get_vocab] on default WordSiv instance."""

    return _default_wordsiv_instance.get_vocab(vocab_name)


def add_vocab(vocab_name: str, vocab: Vocab) -> None:
    """Calls [`add_vocab`][wordsiv.WordSiv.add_vocab] on default WordSiv instance."""

    return _default_wordsiv_instance.add_vocab(vocab_name, vocab)


def number(**kwargs) -> str:
    """Calls [`number`][wordsiv.WordSiv.number] on default WordSiv instance."""

    return _default_wordsiv_instance.number(**kwargs)


def word(**kwargs) -> str:
    """Calls [`word`][wordsiv.WordSiv.word] on default WordSiv instance."""

    return _default_wordsiv_instance.word(**kwargs)


def top_word(*args, **kwargs) -> str:
    """Calls [`top_word`][wordsiv.WordSiv.top_word] on default WordSiv instance."""

    return _default_wordsiv_instance.top_word(*args, **kwargs)


def words(**kwargs) -> list[str]:
    """Calls [`words`][wordsiv.WordSiv.words] on default WordSiv instance."""

    return _default_wordsiv_instance.words(**kwargs)


def top_words(**kwargs) -> list[str]:
    """Calls [`top_words`][wordsiv.WordSiv.top_words] on default WordSiv instance."""

    return _default_wordsiv_instance.top_words(**kwargs)


def sent(**kwargs) -> str:
    """Calls [`sent`][wordsiv.WordSiv.sent] on default WordSiv instance."""

    return _default_wordsiv_instance.sent(**kwargs)


def sents(**kwargs) -> list[str]:
    """Calls [`sents`][wordsiv.WordSiv.sents] on default WordSiv instance."""

    return _default_wordsiv_instance.sents(**kwargs)


def para(**kwargs) -> str:
    """Calls [`para`][wordsiv.WordSiv.para] on default WordSiv instance."""

    return _default_wordsiv_instance.para(**kwargs)


def paras(**kwargs) -> list[str]:
    """Calls [`paras`][wordsiv.WordSiv.paras] on default WordSiv instance."""

    return _default_wordsiv_instance.paras(**kwargs)


def txt(**kwargs) -> str:
    """Calls [`text`][wordsiv.WordSiv.txt] on default WordSiv instance."""

    return _default_wordsiv_instance.txt(**kwargs)


def list_vocabs() -> list[str]:
    """Calls [`list_vocabs`][wordsiv.WordSiv.list_vocabs] on default WordSiv instance."""

    return _default_wordsiv_instance.list_vocabs()
