import io
from functools import lru_cache
import regex
import sys
from io import StringIO

BIG_NUM = 2 ** 10


class FilterError(Exception):
    pass


class SourceEmptyError(Exception):
    pass


class SourceFormatError(Exception):
    pass


class WordCountSource:
    """
    A Source that expects a TSV file with words and counts.

    The file should look like this:
    "koala\t235\ncobra\t123\n"
    """

    def __init__(self, data_file, meta: dict, lines: int = None, test_data=None):

        self.data_file = data_file
        self.meta = meta
        self.lines = lines
        self.test_data = test_data

        # set when loading data, either from meta or data_file
        self.bicameral = self.meta["bicameral"] in ["True", "true"]

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def data(self):
        """
        Read and cache the data from a TSV file, or simple newline-delimited word list.

        :return: a TSV formatted string with words and counts
        """

        rows = []
        if self.test_data is not None:
            # inject a string for testing
            with StringIO(self.test_data) as f:
                for l in f:
                    rows.append(l.strip())  # Add each line stripped of newlines
        else:
            with io.open(self.data_file, "r", encoding="utf8") as f:
                for l in f:
                    rows.append(l.strip())  # Add each line stripped of newlines

        if not rows:
            raise SourceEmptyError(f"No data found in {self.data_file}")

        if not regex.match(r"[[:alpha:]]+\t\d+$", rows[0]) and not regex.match(
            r"[[:alpha:]]+", rows[0]
        ):
            raise SourceFormatError(
                "The source file is formatted incorrectly. "
                "Should be a TSV file with words and counts as columns, or a newline-delimited list of words."
            )

        # Check if the first line has counts
        has_counts = "\t" in rows[0]

        # If there are no counts, update rows to add count of 1
        if not has_counts:
            rows = [f"{line}\t1" for line in rows]  # Add count of 1 to each line

        output = "\n".join(rows)  # Join rows with newlines
        return output

    @lru_cache(maxsize=None)
    def filter_data(
        self,
        glyphs,
        top_k=BIG_NUM,
        case="any",
        min_wl=0,
        max_wl=BIG_NUM,
        wl=None,
        contains=None,
        inner=None,
        startswith=None,
        endswith=None,
        startglyph=None,
        endglyph=None,
        regexp=None,
    ):
        # start with data from the source
        wc_str = self.data

        # filter by case
        wc_list = case_filter(wc_str, case, glyphs, self.bicameral)

        if not wc_list:
            raise FilterError(
                f"No words available after filtering glyphs='{glyphs}' with case='{case}'"
            )

        if startglyph:
            wc_list = [(w, c) for w, c in wc_list if w[0] == startglyph]
            check_wc_empty(wc_list, "startglyph", f" '{startglyph}'")
        elif startswith:
            wc_list = [(w, c) for w, c in wc_list if w.startswith(startswith)]
            check_wc_empty(wc_list, "startswith", f" '{startswith}'")

        if endglyph:
            wc_list = [(w, c) for w, c in wc_list if w[-1] == endglyph]
            check_wc_empty(wc_list, "endglyph", f" '{endglyph}'")
        elif endswith:
            wc_list = [(w, c) for w, c in wc_list if w.endswith(endswith)]
            check_wc_empty(wc_list, "endswith", f" '{endswith}'")

        # filter with contains, inner, startglyph, endglyph
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
            check_wc_empty(wc_list, "contains", f" '{contains}'")

        # filter by word length
        if wl:
            wc_list = [(w, c) for w, c in wc_list if len(w) == wl]
            check_wc_empty(wc_list, "wl", f" '{wl}")
        elif min_wl or max_wl:
            if not max_wl:
                max_wl = BIG_NUM

            wc_list = [(w, c) for w, c in wc_list if min_wl <= len(w) <= max_wl]
            check_wc_empty(wc_list, "min_wl, max_wl", f" '{min_wl}, {max_wl}'")

        # filter with regex
        if regexp:
            wc_list = regex_filter(wc_list, regexp)
            check_wc_empty(wc_list, "regexp", f" '{regexp}")

        # limit number of words if top_k is set
        if top_k:
            wc_list = wc_list[:top_k]

        return tuple(wc_list)


def check_wc_empty(wc_list, filter_name, details=""):
    if not wc_list:
        msg = f"No words available after {filter_name} filter{details}"
        raise FilterError(msg)


def case_filter(wc_str, case, glyphs, bicameral):
    if not bicameral:
        if glyphs:
            return case_regex(wc_str, f"[{glyphs}]")
        else:
            return case_regex(wc_str, "all")
    else:
        if glyphs:
            uc_glyphs = "".join([c for c in glyphs if c.isupper()])
            lc_glyphs = "".join([c for c in glyphs if c.islower()])

        if case == "any":
            if glyphs:
                # case "any" is the default case, and tries to be as flexible as needed
                # we first try to get unmodified words from source (same as "any_og")
                wc_list = case_regex(wc_str, f"[{glyphs}]+")

                # if no matches, get lowercase words from source we can display capitalized with glyphs
                if not wc_list and uc_glyphs and lc_glyphs:
                    wc_list = case_regex(
                        wc_str,
                        f"[{uc_glyphs.lower()}][{lc_glyphs}]*",
                        change_case="cap",
                    )

                # if no matches still, get all words from source we can display uppercase with glyphs (like case='uc')
                if not wc_list and uc_glyphs:
                    wc_list = case_regex(
                        wc_str, f"[{uc_glyphs}{uc_glyphs.lower()}]+", change_case="uc"
                    )
                return wc_list
            else:
                # for case='any' and no glyphs, return all words
                return case_regex(wc_str, "all")
        elif case == "any_og":
            # case "any_og" means any unmodified words from source
            if glyphs:
                # return all source words we can display with glyphs as is
                return case_regex(wc_str, f"[{glyphs}]+")
            else:
                # return all source words
                return case_regex(wc_str, "all")
        elif case == "lc":
            if glyphs:
                # return words that are lowercase in the source and can be displayed with glyphs
                return case_regex(wc_str, f"[{lc_glyphs}]+")
            else:
                # return words that are lowercase in the source
                return case_regex(wc_str, r"\p{Ll}+")
        elif case == "lc_force":
            # we're "forcing" capitalization in that we're tampering with Capital, UC and CamelCase words in source
            if glyphs:
                # return all source words, lowercased, which can be displayed with glyphs
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")
                return case_regex(
                    wc_str, f"[{lc_glyphs}{lc_glyphs.upper()}]+", change_case="lc"
                )
            else:
                # return all source words, lowercased
                return case_regex(wc_str, "all", change_case="lc")
        elif case == "cap":
            if glyphs:
                # return words that are lowercase or capitalized in source, made capitalized, which can be displayed with glyphs
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")

                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")

                return case_regex(
                    wc_str,
                    f"[{uc_glyphs}{uc_glyphs.lower()}][{lc_glyphs}]*",
                    change_case="cap",
                )
            else:
                # return words that are lowercase or capitalized in source, made capitalized
                return case_regex(wc_str, r".\p{Ll}*", change_case="cap")
        elif case == "cap_og":
            if glyphs:
                # return words that are capitalized in the source and can be displayed with glyphs
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")

                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return case_regex(wc_str, f"[{uc_glyphs}][{lc_glyphs}]*")
            else:
                # return words that are capitalized in the source
                return case_regex(wc_str, r"\p{Lu}\p{Ll}*")
        elif case == "cap_force":
            # we're "forcing" capitalization in that we're tampering with UC and CamelCase words in source
            if glyphs:
                # return all source words, made capitalized, which can be displayed with glyphs
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")

                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return case_regex(
                    wc_str,
                    f"[{uc_glyphs}{uc_glyphs.lower()}][{lc_glyphs}{lc_glyphs.upper()}]*",
                    change_case="cap",
                )
            else:
                # return all source words, made capitalized
                return case_regex(wc_str, "all", change_case="cap")
        elif case == "uc":
            if glyphs:
                # return all source words, made uppercase, which can be displayed with glyphs
                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return case_regex(
                    wc_str, f"[{uc_glyphs}{uc_glyphs.lower()}]+", change_case="uc"
                )
            else:
                # return all source words, made uppercase
                return case_regex(wc_str, "all", change_case="uc")
        elif case == "uc_og":
            if glyphs:
                # return words that are uppercase in the source and can be displayed with glyphs
                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return case_regex(wc_str, f"[{uc_glyphs}]+")
            else:
                # return words that are uppercase in the source
                return case_regex(wc_str, r"\p{Lu}+")
        else:
            raise ValueError(f"Invalid case option: {case}")


def regex_filter(wc_list: list[tuple[str, int]], regexp: str) -> list[tuple[str, int]]:
    """
    Filter words using a regular expression.
    """
    pattern = regex.compile(r"^" + regexp + r"\s+\d+$", regex.MULTILINE)
    wc_str = "\n".join(f"{w}\t{c}" for w, c in wc_list)
    lines = regex.findall(pattern, wc_str)

    return [(l.split()[0], int(l.split()[1])) for l in lines]


@lru_cache(maxsize=None)
def case_regex(
    wc_str: str, pattern: str, change_case: str = "none"
) -> list[tuple[str, int]]:

    if pattern == "all":
        lines = wc_str.splitlines()
    else:
        p = regex.compile(fr"^{pattern}\t\d+$", regex.MULTILINE)
        lines = regex.findall(p, wc_str)

    if change_case == "uc":
        return [(l.split()[0].upper(), int(l.split()[1])) for l in lines]
    elif change_case == "lc":
        return [(l.split()[0].lower(), int(l.split()[1])) for l in lines]
    elif change_case == "cap":
        return [(l.split()[0].capitalize(), int(l.split()[1])) for l in lines]
    else:
        return [(l.split()[0], int(l.split()[1])) for l in lines]
