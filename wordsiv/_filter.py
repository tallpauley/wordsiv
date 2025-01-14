"""
Filter words in a wordcount string.
"""

from typing import Literal

from functools import lru_cache
import regex


class FilterError(Exception):
    pass


CaseType = Literal[
    "any",
    "any_og",
    "lc",
    "lc_force",
    "cap",
    "cap_og",
    "cap_force",
    "uc",
    "uc_og",
    "uc_force",
]
"""
Options for setting case via the `case` argument.
See [Letter Case](../guide/filtering-words/#letter-case) in the Guide for detailed descriptions and examples of each
option
"""


@lru_cache(maxsize=None)
def _filter_wordcount(wc_str, bicameral, glyphs=None, case="any", **kwargs):
    if bicameral and glyphs and case == "any":
        try:
            return _filter_all_params(
                wc_str, bicameral, glyphs, case="any_og", **kwargs
            )
        except FilterError:
            try:
                return _filter_all_params(
                    wc_str, bicameral, glyphs, case="cap", **kwargs
                )
            except FilterError:
                return _filter_all_params(
                    wc_str, bicameral, glyphs, case="uc", **kwargs
                )

    elif case == "any":
        return _filter_all_params(wc_str, bicameral, glyphs, case="any_og", **kwargs)
    else:
        return _filter_all_params(wc_str, bicameral, glyphs, case=case, **kwargs)


def _filter_all_params(
    wc_str,
    bicameral,
    glyphs=None,
    case="any",
    min_wl=0,
    max_wl=None,
    wl=None,
    contains=None,
    inner=None,
    startswith=None,
    endswith=None,
    regexp=None,
):
    # it's faster to filter case first, we just need to do it at the end for 'any'
    wc_list_cased = _filter_case(wc_str, case, glyphs, bicameral)
    if not wc_list_cased:
        raise FilterError(f"No words for case='{case}', glyphs='{glyphs}'")
    else:
        wc_str_cased = "\n".join(wc_list_cased)

    wc_tuple = _filter_wl_substr(
        wc_str_cased, min_wl, max_wl, wl, contains, inner, startswith, endswith, regexp
    )
    if not wc_tuple:
        raise FilterError(
            (
                f"No words for min_wl='{min_wl}', max_wl='{max_wl}', wl='{wl}'",
                f"contains='{contains}', inner='{inner}', startswith='{startswith}',",
                f"endswith='{endswith}', regexp='{regexp}'",
            )
        )

    return wc_tuple


def _check_wc_empty(wc_list, filter_name, details=""):
    if not wc_list:
        msg = f"No words available after {filter_name} filter{details}"
        raise FilterError(msg)


def _filter_wl_substr(
    wc_str, min_wl, max_wl, wl, contains, inner, startswith, endswith, regexp
):
    pattern = "^"
    if startswith:
        _check_alpha(startswith, "startswith")
        pattern += rf"(?={startswith}.*)"

    if endswith:
        _check_alpha(endswith, "endswith")
        pattern += rf"(?=.*{endswith}\t)"

    if contains:
        if isinstance(contains, tuple):
            for c in contains:
                _check_alpha(c, "contains")
                pattern += rf"(?=.*{c}.*\t)"
        else:
            _check_alpha(contains, "contains")
            pattern += rf"(?=.*{contains}.*\t)"

    if inner:
        if isinstance(inner, tuple):
            for i in inner:
                _check_alpha(i, "inner")
                pattern += rf"(?=.+{i}.+\t)"
        else:
            _check_alpha(inner, "inner")
            pattern += rf"(?=.+{inner}.+\t)"

    # filter by word length
    if wl:
        _check_int(wl, "wl")
        pattern += rf"(?=.{{{wl}}}\t)"
    elif min_wl or max_wl:
        # min wl is just 0 by default
        _check_int(min_wl, "min_wl")

        # max wl we need an empty string if it's not set
        if not max_wl:
            max_wl_str = ""
        else:
            _check_int(max_wl, "max_wl")
            max_wl_str = max_wl

        pattern += rf"(?=.{{{min_wl},{max_wl_str}}}\t)"

    # filter with regex
    if regexp:
        pattern += rf"(?={regexp}\t)"

    pattern += r".*$"

    compiled = regex.compile(pattern, regex.MULTILINE)
    lines = compiled.findall(wc_str)

    return tuple((line.split()[0], int(line.split()[1])) for line in lines)


def _filter_case(wc_str, case, glyphs, bicameral):
    if not bicameral:
        if glyphs:
            return _findall_recase(wc_str, f"[{glyphs}]+")
        else:
            return wc_str.splitlines()
    else:
        if glyphs:
            uc_glyphs = "".join([c for c in glyphs if c.isupper()])
            lc_glyphs = "".join([c for c in glyphs if c.islower()])

        if case == "any_og":
            # case "any_og" means any unmodified words from vocab
            if glyphs:
                # return all vocab words we can display with glyphs as is
                return _findall_recase(wc_str, f"[{glyphs}]+")
            else:
                # return all vocab words
                return wc_str.splitlines()
        elif case == "lc":
            if glyphs:
                _check_lc_glyphs(lc_glyphs, case)
                # return words that are lowercase in the vocab and can be displayed with glyphs
                return _findall_recase(wc_str, f"[{lc_glyphs}]+")
            else:
                # return words that are lowercase in the vocab
                return _findall_recase(wc_str, r"\p{Ll}+")
        elif case == "lc_force":
            # we're "forcing" capitalization in that we're tampering with Capital, UC and CamelCase words in vocab
            if glyphs:
                # return all vocab words, lowercased, which can be displayed with glyphs
                _check_lc_glyphs(lc_glyphs, case)
                return _findall_recase(
                    wc_str, f"[{lc_glyphs}{lc_glyphs.upper()}]+", change_case="lc"
                )
            else:
                # return all vocab words, lowercased
                return _findall_recase(wc_str, "all", change_case="lc")
        elif case == "cap":
            if glyphs:
                # return words that are lowercase or capitalized in vocab, made capitalized, which can be displayed with glyphs
                _check_lc_glyphs(lc_glyphs, case)
                _check_uc_glyphs(uc_glyphs, case)

                return _findall_recase(
                    wc_str,
                    f"[{uc_glyphs}{uc_glyphs.lower()}][{lc_glyphs}]*",
                    change_case="cap",
                )
            else:
                # return words that are lowercase or capitalized in vocab, made capitalized
                return _findall_recase(wc_str, r".\p{Ll}*", change_case="cap")
        elif case == "cap_og":
            if glyphs:
                # return words that are capitalized in the vocab and can be displayed with glyphs
                _check_lc_glyphs(lc_glyphs, case)
                _check_uc_glyphs(uc_glyphs, case)
                return _findall_recase(wc_str, f"[{uc_glyphs}][{lc_glyphs}]*")
            else:
                # return words that are capitalized in the vocab
                return _findall_recase(wc_str, r"\p{Lu}\p{Ll}*")
        elif case == "cap_force":
            # we're "forcing" capitalization in that we're tampering with UC and CamelCase words in vocab
            if glyphs:
                # return all vocab words, made capitalized, which can be displayed with glyphs
                _check_lc_glyphs(lc_glyphs, case)
                _check_uc_glyphs(uc_glyphs, case)
                return _findall_recase(
                    wc_str,
                    f"[{uc_glyphs}{uc_glyphs.lower()}][{lc_glyphs}{lc_glyphs.upper()}]*",
                    change_case="cap",
                )
            else:
                # return all vocab words, made capitalized
                return _findall_recase(wc_str, "all", change_case="cap")
        elif case == "uc":
            # catch camelcase words
            no_camel = r"(?!.*\p{{Ll}}\p{{Lu}}.*)"
            # catch words like PCIe
            no_double_upper_lower = r"(?!.*\p{Lu}{2,}\p{Ll}.*)"

            if glyphs:
                # return all vocab words, made uppercase, which can be displayed with glyphs
                # no camelcase words, those should not be made uppercase
                _check_uc_glyphs(uc_glyphs, case)
                return _findall_recase(
                    wc_str,
                    no_camel
                    + no_double_upper_lower
                    + f"[{uc_glyphs}{uc_glyphs.lower()}]+",
                    change_case="uc",
                )
            else:
                # return all vocab words, except mixed case words
                return _findall_recase(
                    wc_str,
                    no_camel + no_double_upper_lower + ".*",
                    change_case="uc",
                )
        elif case == "uc_og":
            if glyphs:
                # return words that are uppercase in the vocab and can be displayed with glyphs
                _check_uc_glyphs(uc_glyphs, case)
                return _findall_recase(wc_str, f"[{uc_glyphs}]+")
            else:
                # return words that are uppercase in the vocab
                return _findall_recase(wc_str, r"\p{Lu}+")
        elif case == "uc_force":
            if glyphs:
                # return all vocab words, made uppercase, which can be displayed with glyphs
                # even uppercase camelcase words
                _check_uc_glyphs(uc_glyphs, case)
                return _findall_recase(
                    wc_str,
                    f"[{uc_glyphs}{uc_glyphs.lower()}]+",
                    change_case="uc",
                )
            else:
                # return all vocab words, made uppercase
                return _findall_recase(wc_str, "all", change_case="uc")
        else:
            raise ValueError(f"Invalid case option: {case}")


def _check_int(i, name):
    if not isinstance(i, int):
        raise ValueError(f"{name} must be an integer")


def _check_alpha(s, name):
    if not s.isalpha():
        raise ValueError(f"{name} must be a string of alphabetic characters")


def _check_uc_glyphs(uc_glyphs, case):
    if not uc_glyphs:
        raise FilterError("case='{case}' but no uppercase glyphs found")


def _check_lc_glyphs(lc_glyphs, case):
    if not lc_glyphs:
        raise FilterError("case='{case}' but no lowercase glyphs found")


@lru_cache(maxsize=None)
def _findall_recase(wc_str: str, pattern: str, change_case: str = "none") -> list[str]:
    """
    Find all words in wordcount string that match pattern, and optionally change case.
    """

    if pattern == "all":
        lines = wc_str.splitlines()
    else:
        p = regex.compile(rf"^{pattern}\t\d+$", regex.MULTILINE)
        lines = regex.findall(p, wc_str)

    # we can actually just transform case of whole line since it ignores whitespace
    # and numerals
    if change_case == "uc":
        return [line.upper() for line in lines]
    elif change_case == "lc":
        return [line.lower() for line in lines]
    elif change_case == "cap":
        return [line.capitalize() for line in lines]
    else:
        return list(lines)
