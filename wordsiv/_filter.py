"""
Filter words in a wordcount string.
"""

from typing import Literal

from functools import lru_cache
import regex

_BIG_NUM = 2**10


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
]


@lru_cache(maxsize=None)
def _filter_wordcount(
    wordcount_str,
    bicameral,
    glyphs=None,
    case="any",
    min_wl=0,
    max_wl=_BIG_NUM,
    wl=None,
    contains=None,
    inner=None,
    startswith=None,
    endswith=None,
    regexp=None,
):
    # filter by case
    wc_list = _filter_case(wordcount_str, case, glyphs, bicameral)

    if not wc_list:
        raise FilterError(
            f"No words available after filtering glyphs='{glyphs}' with case='{case}'"
        )

    if startswith:
        sw_len = len(startswith)
        wc_list = [(w, c) for w, c in wc_list if w[:sw_len] == startswith]
        _check_wc_empty(wc_list, "startswith", f" '{startswith}'")

    if endswith:
        ew_len = len(endswith)
        wc_list = [(w, c) for w, c in wc_list if w[-ew_len:] == endswith]
        _check_wc_empty(wc_list, "endswith", f" '{endswith}'")

    # filter with contains, inner
    if inner:
        contains = inner

    if contains:
        if type(contains) is str:
            contains = [contains]

        for contains_search in contains:
            if inner:
                wc_list = [(w, c) for w, c in wc_list if contains_search in w[1:-1]]
            else:
                wc_list = [(w, c) for w, c in wc_list if contains_search in w]
        _check_wc_empty(wc_list, "contains", f" '{contains}'")

    # filter by word length
    if wl:
        wc_list = [(w, c) for w, c in wc_list if len(w) == wl]
        _check_wc_empty(wc_list, "wl", f" '{wl}")
    elif min_wl or max_wl:
        if not max_wl:
            max_wl = _BIG_NUM

        wc_list = [(w, c) for w, c in wc_list if min_wl <= len(w) <= max_wl]
        _check_wc_empty(wc_list, "min_wl, max_wl", f" '{min_wl}, {max_wl}'")

    # filter with regex
    if regexp:
        wc_list = _filter_regex(wc_list, regexp)
        _check_wc_empty(wc_list, "regexp", f" '{regexp}")

    return tuple(wc_list)


def _check_wc_empty(wc_list, filter_name, details=""):
    if not wc_list:
        msg = f"No words available after {filter_name} filter{details}"
        raise FilterError(msg)


def _filter_case(wc_str, case, glyphs, bicameral):
    if not bicameral:
        if glyphs:
            return _findall_recase(wc_str, f"[{glyphs}]+")
        else:
            return _findall_recase(wc_str, "all")
    else:
        if glyphs:
            uc_glyphs = "".join([c for c in glyphs if c.isupper()])
            lc_glyphs = "".join([c for c in glyphs if c.islower()])

        if case == "any":
            if glyphs:
                # case "any" is the default case, and tries to be as flexible as needed
                # we first try to get unmodified words from vocab (same as "any_og")
                wc_list = _findall_recase(wc_str, f"[{glyphs}]+")

                # if no matches, get lowercase words from vocab we can display capitalized with glyphs
                if not wc_list and uc_glyphs and lc_glyphs:
                    wc_list = _findall_recase(
                        wc_str,
                        f"[{uc_glyphs.lower()}][{lc_glyphs}]*",
                        change_case="cap",
                    )

                # if no matches still, get all words from vocab we can display uppercase with glyphs (like case='uc')
                if not wc_list and uc_glyphs:
                    wc_list = _findall_recase(
                        wc_str, f"[{uc_glyphs}{uc_glyphs.lower()}]+", change_case="uc"
                    )
                return wc_list
            else:
                # for case='any' and no glyphs, return all words
                return _findall_recase(wc_str, "all")
        elif case == "any_og":
            # case "any_og" means any unmodified words from vocab
            if glyphs:
                # return all vocab words we can display with glyphs as is
                return _findall_recase(wc_str, f"[{glyphs}]+")
            else:
                # return all vocab words
                return _findall_recase(wc_str, "all")
        elif case == "lc":
            if glyphs:
                # return words that are lowercase in the vocab and can be displayed with glyphs
                return _findall_recase(wc_str, f"[{lc_glyphs}]+")
            else:
                # return words that are lowercase in the vocab
                return _findall_recase(wc_str, r"\p{Ll}+")
        elif case == "lc_force":
            # we're "forcing" capitalization in that we're tampering with Capital, UC and CamelCase words in vocab
            if glyphs:
                # return all vocab words, lowercased, which can be displayed with glyphs
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")
                return _findall_recase(
                    wc_str, f"[{lc_glyphs}{lc_glyphs.upper()}]+", change_case="lc"
                )
            else:
                # return all vocab words, lowercased
                return _findall_recase(wc_str, "all", change_case="lc")
        elif case == "cap":
            if glyphs:
                # return words that are lowercase or capitalized in vocab, made capitalized, which can be displayed with glyphs
                if not lc_glyphs:
                    raise FilterError(f"case='{case}' but no lowercase glyphs found")

                if not uc_glyphs:
                    raise FilterError(f"case='{case}' but no uppercase glyphs found")

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
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")

                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return _findall_recase(wc_str, f"[{uc_glyphs}][{lc_glyphs}]*")
            else:
                # return words that are capitalized in the vocab
                return _findall_recase(wc_str, r"\p{Lu}\p{Ll}*")
        elif case == "cap_force":
            # we're "forcing" capitalization in that we're tampering with UC and CamelCase words in vocab
            if glyphs:
                # return all vocab words, made capitalized, which can be displayed with glyphs
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")

                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return _findall_recase(
                    wc_str,
                    f"[{uc_glyphs}{uc_glyphs.lower()}][{lc_glyphs}{lc_glyphs.upper()}]*",
                    change_case="cap",
                )
            else:
                # return all vocab words, made capitalized
                return _findall_recase(wc_str, "all", change_case="cap")
        elif case == "uc":
            if glyphs:
                # return all vocab words, made uppercase, which can be displayed with glyphs
                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return _findall_recase(
                    wc_str, f"[{uc_glyphs}{uc_glyphs.lower()}]+", change_case="uc"
                )
            else:
                # return all vocab words, made uppercase
                return _findall_recase(wc_str, "all", change_case="uc")
        elif case == "uc_og":
            if glyphs:
                # return words that are uppercase in the vocab and can be displayed with glyphs
                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return _findall_recase(wc_str, f"[{uc_glyphs}]+")
            else:
                # return words that are uppercase in the vocab
                return _findall_recase(wc_str, r"\p{Lu}+")
        else:
            raise ValueError(f"Invalid case option: {case}")


def _filter_regex(wc_list: list[tuple[str, int]], regexp: str) -> list[tuple[str, int]]:
    """
    Filter words using a regular expression.
    """
    pattern = regex.compile(r"^" + regexp + r"\s+\d+$", regex.MULTILINE)
    wc_str = "\n".join(f"{w}\t{c}" for w, c in wc_list)
    lines = regex.findall(pattern, wc_str)

    return [(line.split()[0], int(line.split()[1])) for line in lines]


@lru_cache(maxsize=None)
def _findall_recase(
    wc_str: str, pattern: str, change_case: str = "none"
) -> list[tuple[str, int]]:
    """
    Find all words in wordcount string that match pattern, and optionally change case.
    """

    if pattern == "all":
        lines = wc_str.splitlines()
    else:
        p = regex.compile(rf"^{pattern}\t\d+$", regex.MULTILINE)
        lines = regex.findall(p, wc_str)

    if change_case == "uc":
        return [(line.split()[0].upper(), int(line.split()[1])) for line in lines]
    elif change_case == "lc":
        return [(line.split()[0].lower(), int(line.split()[1])) for line in lines]
    elif change_case == "cap":
        return [(line.split()[0].capitalize(), int(line.split()[1])) for line in lines]
    else:
        return [(line.split()[0], int(line.split()[1])) for line in lines]
