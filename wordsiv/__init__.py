"""WordSiv is a Python library for generating text for an incomplete typeface."""

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
from . import _vocab_data

__all__ = [
    "WordSiv",
    "Vocab",
    "FilterError",
    "CaseType",
    "VocabFormatError",
    "VocabEmptyError",
]

log = logging.getLogger(__name__)

DEFAULT_VOCABS = {
    "ar": ("ar_subs_meta.json", "ar_subs.tsv"),
    "en": ("en_books_meta.json", "en_books.tsv"),
    "es": ("es_subs_meta.json", "es_subs.tsv"),
    "fa": ("fa_subs_meta.json", "fa_subs.tsv"),
}


@lru_cache(maxsize=None)
def _accumulate_weights(counts: tuple[float, ...]) -> tuple[float, ...]:
    """
    Accumulate a tuple of numeric weights and return the cumulative sums and cache the
    result.

    Args:
        counts (tuple[float, ...]): A tuple of numeric values representing weights.

    Returns:
        tuple[float, ...]: A tuple of cumulative sums of the input weights.
    """
    return tuple(accumulate(counts))


@lru_cache(maxsize=None)
def _split_wordcount(
    word_count: tuple[tuple[str, int], ...],
) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """
    Split a tuple of (word, count) pairs into two tuples—one of words, one of counts.
    Cache results.

    Args:
        word_count (tuple[tuple[str, int], ...]): A tuple of (word, count) pairs.

    Returns:
        tuple[tuple[str, ...], tuple[int, ...]]:
            - A tuple of words.
            - A tuple of corresponding counts.
    """
    return tuple(i[0] for i in word_count), tuple(i[1] for i in word_count)


@lru_cache(maxsize=None)
def _interpolate_counts(counts: tuple[float, ...], rnd: float) -> tuple[float, ...]:
    """
    Interpolate counts with a random distribution factor.

    Args:
        counts (tuple[float, ...]): A tuple of numeric counts.
        rnd (float): A randomness factor between 0 and 1.

    Returns:
        tuple[float, ...]: A tuple of adjusted counts.
    """
    max_count = max(counts)
    adjusted_counts = tuple((1 - rnd) * c + rnd * max_count for c in counts)
    return adjusted_counts


def _sample_word(
    word_count: tuple[tuple[str, float], ...], rand: random.Random, rnd: float
) -> str:
    """
    Sample a word from a list of (word, count) pairs, using counts as weights.

    Args:
        word_count (tuple[tuple[str, float], ...]): A tuple of (word, count) pairs.
        rand (random.Random): A `random.Random` instance.
        rnd (float): A randomness factor between 0 and 1.

    Returns:
        str: A randomly chosen word from `word_count`.
    """
    words, counts = _split_wordcount(word_count)
    adjusted_counts = _interpolate_counts(counts, rnd)
    accumulated_counts = _accumulate_weights(adjusted_counts)

    return rand.choices(words, cum_weights=accumulated_counts)[0]


class WordSiv:
    """The main WordSiv object which uses Vocabs to generate text.

    This object serves as the main interface for generating text. It can hold multiple
    vocabulary objects, store default settings (like default glyphs and vocab), and
    expose high-level methods that produce words, sentences, paragraphs, and more.

    Args:
        vocab (str | None): The name of the default Vocab.
        glyphs (str | None): The default set of glyphs that constrains the words
            generated.
        add_default_vocabs (bool): Whether to add the default Vocabs defined in
            `DEFAULT_VOCABS`.
        raise_errors (bool): Whether to raise errors or fail gently.
        seed (int | None): Seed for the random number generator.

    Attributes:
        vocab (str | None): The name of the default Vocab.
        glyphs (str | None): The default set of glyphs that constrains the words
            generated.
        raise_errors (bool): Whether to raise errors or fail gently.
        _vocab_lookup (dict[str, Vocab]): A dictionary of vocab names to `Vocab`
            objects.
        _rand (random.Random): A `random.Random` instance.
    """

    def __init__(
        self,
        vocab: str | None = None,
        glyphs: str | None = None,
        add_default_vocabs: bool = True,
        raise_errors: bool = False,
        seed=None,
    ):
        self.vocab = vocab
        self.glyphs = glyphs
        self.raise_errors = raise_errors
        self._vocab_lookup: dict[str, Vocab] = {}

        if add_default_vocabs:
            self._add_default_vocabs()

        self._rand = random.Random()

        if seed is not None:
            self.seed(seed)

    def seed(self, seed: float | str | None = None) -> None:
        """
        Seed the random number generator for reproducible results.

        Args:
            seed (float | str | None): The seed value used to initialize the random
                number generator.

        Returns:
            None
        """
        self._rand.seed(seed)

    def add_vocab(self, vocab_name: str, vocab: Vocab) -> None:
        """
        Add a `Vocab` object to this `WordSiv` instance under a given name.

        Args:
            vocab_name (str): The unique identifier for this Vocab.
            vocab (Vocab): The `Vocab` object to be associated with `vocab_name`.

        Returns:
            None
        """
        self._vocab_lookup[vocab_name] = vocab

    def _add_default_vocabs(self) -> None:
        """
        Initialize and add the default Vocabs to this `WordSiv` instance.

        The default vocabularies are specified in the `DEFAULT_VOCABS` dictionary, which
        maps a short code (e.g., 'en', 'es') to the meta and data filenames. This method
        initializes each Vocab (however, the data is loaded lazily).
        """
        for vocab_name, (meta_file, data_file) in DEFAULT_VOCABS.items():
            meta_path = resources.files(_vocab_data) / meta_file
            with meta_path.open("r", encoding="utf8") as f:
                meta = json.load(f)

            data_path = resources.files(_vocab_data) / data_file
            vocab = Vocab(
                meta["lang"], bool(meta["bicameral"]), meta=meta, data_file=data_path
            )
            self.add_vocab(vocab_name, vocab)

    def get_vocab(self, vocab_name: str | None = None) -> Vocab:
        """
        Retrieve a `Vocab` by name, or return the default Vocab if `vocab_name` is None.

        Args:
            vocab_name (str | None): The name of the Vocab to retrieve. If None,
                use the default `self.vocab`.

        Returns:
            Vocab: The `Vocab` object corresponding to `vocab_name`.

        Raises:
            ValueError: If no `vocab_name` is provided and no default is set.
        """
        if vocab_name:
            return self._vocab_lookup[vocab_name]
        else:
            if self.vocab:
                return self._vocab_lookup[self.vocab]
            else:
                raise ValueError("Error: no vocab specified")

    def list_vocabs(self) -> list[str]:
        """
        Return a list of all available Vocab names.

        Returns:
            list[str]: A list of all registered Vocab names in this `WordSiv`.
        """
        return list(self._vocab_lookup.keys())

    def number(
        self,
        seed: float | str | None = None,
        glyphs: str | None = None,
        wl: int | None = None,
        min_wl: int = 1,
        max_wl: int = 4,
        raise_errors: bool = False,
    ) -> str:
        """
        Generate a random numeric string (made of digits) constrained by glyphs and
        other parameters.

        Args:
            seed (float | str | None): Seed the random number generator if seed is not
                None.
            glyphs (str | None): A string of allowed glyphs. If None, uses the default
                glyphs of this `WordSiv` instance.
            wl (int | None): Exact length of the generated numeric string. If None, a
                random length between `min_wl` and `max_wl` is chosen.
            min_wl (int): Minimum length of the numeric string. Defaults to 1.
            max_wl (int): Maximum length of the numeric string. Defaults to 4.
            raise_errors (bool): Whether to raise an error if no numerals are available.

        Returns:
            str: A randomly generated string consisting of numerals.

        Raises:
            ValueError: If `min_wl` is greater than `max_wl`.
            FilterError: If no numerals are available in `glyphs` and `raise_errors` is
                True.
        """
        glyphs = self.glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors

        if seed is not None:
            self._rand.seed(seed)

        if wl:
            length = wl
        else:
            if min_wl > max_wl:
                raise ValueError("'min_wl' must be less than or equal to 'max_wl'")
            length = self._rand.randint(min_wl, max_wl)

        available_numerals = "".join(str(n) for n in range(0, 10))
        if glyphs:
            available_numerals = "".join(n for n in available_numerals if n in glyphs)

            if not available_numerals:
                if raise_errors:
                    raise FilterError("No numerals available in glyphs")
                else:
                    log.warning("No numerals available in glyphs")
                    return ""

        return "".join(self._rand.choice(available_numerals) for _ in range(length))

    def word(
        self,
        vocab: str | None = None,
        glyphs: str | None = None,
        seed: float | str | None = None,
        rnd: float = 0,
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
    ) -> str:
        """
        Generate a random word that meets a variety of constraints, such as glyphs,
        length, regex filters, etc.

        Args:
            vocab (str | None): Name of the Vocab to use. If None, uses default Vocab.
            glyphs (str | None): A string of allowed glyphs. If None, uses default
                glyphs.
            seed (float | str | None): Seed the random number generator if seed is not
                None.
            rnd (float): Randomness factor in [0, 1] for selecting among the top words.
            case (CaseType): Desired case of the output word (e.g., 'upper', 'lower',
                'any').
            top_k (int): If > 0, only consider the top K words by frequency.
            min_wl (int): Minimum word length.
            max_wl (int | None): Maximum word length. If None, no maximum is applied.
            wl (int | None): Exact word length. If None, no exact length is enforced.
            contains (str | Sequence[str] | None): Substring(s) that must appear in the
                word.
            inner (str | Sequence[str] | None): Substring(s) that must appear, but not
                at the start or end of the word.
            startswith (str | None): Required starting substring.
            endswith (str | None): Required ending substring.
            regexp (str | None): A regular expression that the word must match.
            raise_errors (bool): Whether to raise filtering errors or fail gently.

        Returns:
            str: A randomly generated word meeting the specified constraints (or an
                empty string on failure if `raise_errors` is False).

        Raises:
            ValueError: If `rnd` is not in [0, 1].
            FilterError: If filtering yields no results and `raise_errors` is True.
            VocabFormatError: If the underlying Vocab data is malformed.
            VocabEmptyError: If the underlying Vocab is empty.
        """
        glyphs = self.glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors
        vocab_obj = self.get_vocab(vocab)

        if not (0 <= rnd <= 1):
            raise ValueError("'rnd' must be between 0 and 1")

        if seed is not None:
            self._rand.seed(seed)

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

        if top_k:
            wc_list = wc_list[:top_k]

        return _sample_word(wc_list, self._rand, rnd)

    def top_word(
        self,
        vocab: str | None = None,
        glyphs: str | None = None,
        seed: float | str | None = None,
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
    ) -> str:
        """
        Retrieve the most common (or nth most common) word from the Vocab, subject to
        filtering constraints.

        Args:
            vocab (str | None): Name of the Vocab to use. If None, use the default
                Vocab.
            glyphs (str | None): Whitelisted glyphs to filter words. If None, uses
                default.
            seed (float | str | None): Seed the random number generator if seed is
                not None.
            idx (int): Index of the desired word in the frequency-sorted list
                (0-based).
            case (CaseType): Desired case form for the word (e.g., 'lower', 'upper',
                'any').
            min_wl (int): Minimum word length.
            max_wl (int | None): Maximum word length. If None, no maximum.
            wl (int | None): Exact word length. If None, no exact length filter.
            contains (str | Sequence[str] | None): Substring(s) that must appear in
                the word.
            inner (str | Sequence[str] | None): Substring(s) that must appear in the
                interior.
            startswith (str | None): Substring that the word must start with.
            endswith (str | None): Substring that the word must end with.
            regexp (str | Sequence[str] | None): Regex pattern(s) that the word must
                match.
            raise_errors (bool): Whether to raise errors on filter or index failures.

        Returns:
            str: The nth most common word that meets the constraints (or an empty string
            on failure if `raise_errors` is False).

        Raises:
            FilterError: If filtering fails (no words match) and `raise_errors` is True.
            ValueError: If no default vocab is set when `vocab` is None.
            IndexError: If `idx` is out of range after filtering and `raise_errors` is True.
        """
        glyphs = self.glyphs if not glyphs else glyphs
        raise_errors = self.raise_errors if not raise_errors else raise_errors
        vocab_obj = self.get_vocab(self.vocab) if not vocab else self.get_vocab(vocab)

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
        min_n_words: int = 10,
        max_n_words: int = 20,
        numbers: float = 0,
        cap_first: bool | None = None,
        case: CaseType = "any",
        rnd: float = 0,
        **word_num_kwargs,
    ) -> list[str]:
        """
        Generate a list of words (and optionally numbers) according to the specified
        parameters.

        This method will produce `n_words` tokens, each of which may be a word or a
        number (digit string), depending on the `numbers` ratio. It can also
        automatically handle capitalization of the first token if `cap_first` is True
        (or inferred).

        Args:
            vocab (str | None): Name of the Vocab to use. If None, uses the default
                Vocab.
            glyphs (str | None): Allowed glyph set. If None, uses the default glyphs.
            seed (any): Seed for the random number generator. If None, current state is
                used.
            n_words (int | None): Exact number of tokens to generate. If None, randomly
                choose between `min_n_words` and `max_n_words`.
            min_n_words (int): Minimum number of tokens if `n_words` is not specified.
            max_n_words (int): Maximum number of tokens if `n_words` is not specified.
            numbers (float): A value in [0, 1] that determines the probability of
                generating a numeric token instead of a word.
            cap_first (bool | None): If True, capitalize the first word (if `case` is
                "any"). If None, automatically decide based on glyphs availability.
            case (CaseType): Desired case form for the words ("any", "lower", "upper",
                etc.).
            rnd (float): Randomness factor for word selection, in [0, 1].
            **word_num_kwargs: Additional keyword arguments passed along to `word` or
                `number`.

        Returns:
            list[str]: A list of randomly generated tokens (words or numbers).

        Raises:
            ValueError: If `numbers` is not in [0, 1].
        """
        glyphs = self.glyphs if not glyphs else glyphs

        if seed is not None:
            self._rand.seed(seed)

        if not n_words:
            n_words = self._rand.randint(min_n_words, max_n_words)

        if cap_first is None:
            if glyphs:
                # If constrained glyphs, only capitalize if uppercase letters exist
                cap_first = any(c for c in glyphs if c.isupper())
            else:
                # Otherwise, default to capitalize the first word
                cap_first = True

        if not (0 <= numbers <= 1):
            raise ValueError("'numbers' must be between 0 and 1")

        word_list = []
        last_w = None
        for i in range(n_words):
            if cap_first and case == "any" and i == 0:
                word_case: CaseType = "cap"
            else:
                word_case = case

            token_type = self._rand.choices(
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

                # Try once more to avoid consecutive repeats
                if w == last_w:
                    w = self.word(
                        vocab=vocab,
                        glyphs=glyphs,
                        case=word_case,
                        rnd=rnd,
                        **word_num_kwargs,
                    )

                if w:
                    word_list.append(w)
                    last_w = w
            else:
                # token_type == "number"
                w = self.number(glyphs=glyphs, **word_num_kwargs)

                if w:
                    word_list.append(w)
                    last_w = w

        return word_list

    def top_words(
        self,
        glyphs: str | None = None,
        vocab: str | None = None,
        n_words: int = 10,
        idx: int = 0,
        case: CaseType = "any",
        min_wl: int = 1,
        max_wl: int | None = None,
        wl: int | None = None,
        contains: str | Sequence[str] | None = None,
        inner: str | Sequence[str] | None = None,
        startswith: str | None = None,
        endswith: str | None = None,
        regexp: str | None = None,
        raise_errors: bool = False,
    ) -> list[str]:
        """
        Retrieve the top `n_words` from the Vocab, starting at index `idx`, subject to
        filtering constraints.

        Args:
            glyphs (str | None): Allowed glyph set. If None, uses default glyphs.
            vocab (str | None): Name of the Vocab to use. If None, use the default Vocab.
            n_words (int): Number of words to return.
            idx (int): The index at which to start returning words (0-based).
            case (CaseType): Desired case form ("any", "upper", "lower", etc.).
            min_wl (int): Minimum word length. Defaults to 1.
            max_wl (int | None): Maximum word length. If None, no maximum is applied.
            wl (int | None): Exact word length. If None, no exact length filter.
            contains (str | Sequence[str] | None): Substring(s) that must appear.
            inner (str | Sequence[str] | None): Substring(s) that must appear, not at edges.
            startswith (str | None): Required starting substring.
            endswith (str | None): Required ending substring.
            regexp (str | None): Regex pattern(s) to match.
            raise_errors (bool): Whether to raise errors or fail gently.

        Returns:
            list[str]: A list of up to `n_words` words, in descending frequency order.

        Raises:
            FilterError: If filtering fails (no words match) and `raise_errors` is True.
        """
        glyphs = self.glyphs if not glyphs else glyphs
        vocab_obj = self.get_vocab(self.vocab) if not vocab else self.get_vocab(vocab)

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
                log.warning("No words found at idx '%s'", idx)
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
    ) -> str:
        """
        Generate a single sentence, optionally punctuated, using words (and/or numbers).

        A sentence is created by calling `words(...)`, then (optionally) punctuating the
        resulting list.

        Args:
            vocab (str | None): Name of the Vocab to use. If None, use the default Vocab.
            glyphs (str | None): Allowed glyphs. If None, uses default glyphs.
            seed (any): Seed for the random number generator. If None, current state is used.
            punc (bool): Whether to add punctuation to the sentence.
            rnd_punc (float): A randomness factor between 0 and 1 that adjusts the punctuation
                frequency or distribution.
            **words_kwargs: Additional keyword arguments passed to `words(...)`.

        Returns:
            str: A single sentence, optionally with punctuation.

        Raises:
            ValueError: If `rnd_punc` is not in [0, 1].
        """
        glyphs = self.glyphs if not glyphs else glyphs
        vocab_obj = self.get_vocab(vocab)

        if seed is not None:
            self._rand.seed(seed)

        word_list = self.words(
            glyphs=glyphs,
            vocab=vocab,
            **words_kwargs,
        )

        if punc:
            if not (0 <= rnd_punc <= 1):
                raise ValueError("'rnd_punc' must be between 0 and 1")

            if vocab_obj.punctuation:
                punctuation = vocab_obj.punctuation
            else:
                try:
                    punctuation = DEFAULT_PUNCTUATION[vocab_obj.lang]
                except KeyError:
                    # If no default punctuation is found, return unpunctuated sentence
                    return " ".join(word_list)

            return _punctuate(
                punctuation,
                self._rand,
                word_list,
                glyphs,
                rnd_punc,
            )
        else:
            return " ".join(word_list)

    def sents(
        self,
        seed=None,
        min_n_sents: int = 3,
        max_n_sents: int = 5,
        n_sents: int | None = None,
        **sent_kwargs,
    ) -> list[str]:
        """
        Generate multiple sentences with `sent(...)`, returned as a list.

        Args:
            seed (float | str | None): Seed the random number generator if seed is not
                None.
            min_n_sents (int): Minimum number of sentences to produce if `n_sents` is None.
            max_n_sents (int): Maximum number of sentences to produce if `n_sents` is None.
            n_sents (int | None): If specified, exactly that many sentences are produced.
            **sent_kwargs: Additional keyword arguments passed to `sent(...)`.

        Returns:
            list[str]: A list of generated sentences.
        """
        if seed is not None:
            self._rand.seed(seed)

        if not n_sents:
            n_sents = self._rand.randint(min_n_sents, max_n_sents)

        return [self.sent(**sent_kwargs) for _ in range(n_sents)]

    def para(
        self,
        seed=None,
        sent_sep: str = " ",
        **sents_kwargs,
    ) -> str:
        """
        Generate a paragraph by creating multiple sentences with `sents(...)` and
        joining them with `sent_sep`.

        Args:
            seed (float | str | None): Seed the random number generator if seed is not
                None.
            sent_sep (str): The string used to join sentences.
             **sents_kwargs: Keyword arguments passed to `sents(...)`.

        Returns:
            str: A single paragraph containing multiple sentences.
        """
        if seed is not None:
            self._rand.seed(seed)

        return sent_sep.join(self.sents(**sents_kwargs))

    def paras(
        self,
        seed=None,
        n_paras: int = 3,
        **para_kwargs,
    ) -> list[str]:
        """
        Generate multiple paragraphs with `para(...)`, returned as a list.

        Args:
            seed (float | str | None): Seed the random number generator if seed is not
                None.
            n_paras (int): Number of paragraphs to generate.
            **para_kwargs: Additional keyword arguments passed to `para(...)`.

        Returns:
            list[str]: A list of paragraphs.
        """
        if seed is not None:
            self._rand.seed(seed)

        return [self.para(**para_kwargs) for _ in range(n_paras)]

    def text(
        self,
        seed: float | str | None = None,
        para_sep: str = "\n\n",
        **paras_kwargs,
    ) -> str:
        """
        Generate multiple paragraphs of text, calling `paras(...)` and joining them with
        `para_sep`.

        Args:
            seed (float | str | None): Seed the random number generator if seed is not
                None.
            para_sep (str): The string used to separate paragraphs in the final text.
            **paras_kwargs: Additional keyword arguments passed to `paras(...)`.

        Returns:
            str: A string containing multiple paragraphs of text, separated by
                `para_sep`.
        """
        if seed is not None:
            self._rand.seed(seed)

        return para_sep.join(self.paras(**paras_kwargs))
