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
        num_top=BIG_NUM,
        case="any",
        min_wl=0,
        max_wl=BIG_NUM,
        wl=None,
        contains=None,
        startswith=None,
        endswith=None,
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

        # filter by word length
        if wl:
            wc_list = [(w, c) for w, c in wc_list if len(w) == wl]
            check_wc_empty(wc_list, "min_wl, max_wl, wl")
        elif min_wl or max_wl:
            if not max_wl:
                max_wl = BIG_NUM

            wc_list = [(w, c) for w, c in wc_list if min_wl <= len(w) <= max_wl]
            check_wc_empty(wc_list, "min_wl, max_wl, wl")

        # filter with contains, startswith, endswith
        if contains:
            if type(contains) is str:
                contains = [contains]

            for contains_search in contains:
                wc_list = [(w, c) for w, c in wc_list if contains_search in w]
                check_wc_empty(wc_list, "contains")

        if startswith:
            wc_list = [(w, c) for w, c in wc_list if w.startswith(startswith)]
            check_wc_empty(wc_list, "startswith")

        if endswith:
            wc_list = [(w, c) for w, c in wc_list if w.endswith(endswith)]
            check_wc_empty(wc_list, "endswith")

        # filter with regex
        if regexp:
            wc_list = regex_filter(wc_list, regexp)
            check_wc_empty(wc_list, "regexp")

        # limit number of words if num_top is set
        if num_top:
            wc_list = wc_list[:num_top]

        return tuple(wc_list)


def check_wc_empty(wc_list, filter_name):
    if not wc_list:
        raise FilterError(f"No words available after {filter_name} filter")


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
                wc_list = case_regex(wc_str, f"[{glyphs}]+")
                if not wc_list and uc_glyphs and lc_glyphs:
                    wc_list = case_regex(
                        wc_str,
                        f"[{uc_glyphs}{uc_glyphs.lower()}][{lc_glyphs}]*",
                        change_case="cap",
                    )
                if not wc_list and uc_glyphs:
                    wc_list = case_regex(
                        wc_str, f"[{uc_glyphs}{uc_glyphs.lower()}]+", change_case="uc"
                    )
                return wc_list
            else:
                return case_regex(wc_str, "all")
        elif case == "any_og":
            if glyphs:
                return case_regex(wc_str, f"[{glyphs}]+")
            else:
                return case_regex(wc_str, "all")
        elif case == "lc":
            if glyphs:
                return case_regex(wc_str, f"[{lc_glyphs}]+")
            else:
                return case_regex(wc_str, r"\p{Ll}+")
        elif case == "lc_force":
            if glyphs:
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")
                return case_regex(
                    wc_str, f"[{lc_glyphs}{lc_glyphs.upper()}]+", change_case="lc"
                )
            else:
                return case_regex(wc_str, "all", change_case="lc")
        elif case == "cap":
            if glyphs:
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
                return case_regex(wc_str, r".\p{Ll}*", change_case="cap")
        elif case == "cap_og":
            if glyphs:
                if not lc_glyphs:
                    raise FilterError("case='{case}' but no lowercase glyphs found")

                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return case_regex(wc_str, f"[{uc_glyphs}][{lc_glyphs}]*")
            else:
                return case_regex(wc_str, r"\p{Lu}\p{Ll}*")
        elif case == "cap_force":
            if glyphs:
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
                return case_regex(wc_str, "all", change_case="cap")
        elif case == "uc":
            if glyphs:
                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return case_regex(
                    wc_str, f"[{uc_glyphs}{uc_glyphs.lower()}]+", change_case="uc"
                )
            else:
                return case_regex(wc_str, "all", change_case="uc")
        elif case == "uc_og":
            if glyphs:
                if not uc_glyphs:
                    raise FilterError("case='{case}' but no uppercase glyphs found")
                return case_regex(wc_str, f"[{uc_glyphs}]+")
            else:
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
