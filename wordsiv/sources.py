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
        case=None,
        min_wl=0,
        max_wl=BIG_NUM,
        wl=None,
        contains=None,
        startswith=None,
        endswith=None,
        regexp=None,
        respect_case=True,
    ):
        # start with data from the source
        wc_str = self.data

        # filter TSV string based on case type
        # output of each filter_ function is a list of tuples (word, count)
        if not self.bicameral:
            wc_list = filter_caseless(wc_str, glyphs)
        elif case == None:
            # filter caseless matches words in the word list that can be spelled as is with glyphs
            wc_list = filter_caseless(wc_str, glyphs)
            if not wc_list:
                # if filter caseless is giving us nothing, filter_cap matches words that can be capitalized with glyphs
                wc_list = filter_cap(wc_str, glyphs, respect_case=respect_case)
            if not wc_list:
                # if filter caseless and filter_cap are giving us nothing, filter_uc matches words that can be uppercased with glyphs
                wc_list = filter_uc(wc_str, glyphs)
            if not wc_list and not respect_case:
                # if filter caseless and filter_cap are giving us nothing, filter_uc matches words that can be uppercased with glyphs
                wc_list = filter_lc(wc_str, glyphs, respect_case=respect_case)
        elif case == "uc":
            wc_list = filter_uc(wc_str, glyphs)
        elif case == "lc":
            wc_list = filter_lc(wc_str, glyphs, respect_case=respect_case)
        elif case == "cap":
            wc_list = filter_cap(wc_str, glyphs, respect_case=respect_case)
        else:
            raise ValueError(f"Invalid case option: {case}")

        if not wc_list:
            raise FilterError(
                f"No words available after filtering glyphs='{glyphs}' with case='{case}' and respect_case='{respect_case}'"
            )

        # filter by word length
        if min_wl or max_wl != BIG_NUM or wl:
            if wl:
                min_wl = wl
                max_wl = wl

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


def filter_uc(wc_str: str, glyphs: str) -> list[tuple[str, int]]:
    """
    Match words that are uppercase (or can be uppercased) and can be spelled with glyphs
    """
    if glyphs:
        uc_glyphs = "".join([c for c in glyphs if c.isupper()])
        if not uc_glyphs:
            return []
        pattern = fr"^[{uc_glyphs}{uc_glyphs.lower()}]+\s+\d+$"
    else:
        pattern = r"^.+\s+\d+$"  # Any word can be made uppercase
    lines = regex.findall(regex.compile(pattern, regex.MULTILINE), wc_str)
    return [(l.split()[0].upper(), int(l.split()[1])) for l in lines]


def filter_lc(wc_str: str, glyphs: str, respect_case: bool) -> list[tuple[str, int]]:
    """
    Match words that are lowercase and can be spelled with glyphs
    """
    if glyphs:
        lc_glyphs = "".join([c for c in glyphs if c.islower()])
        if not lc_glyphs:
            return []
        search_glyphs = lc_glyphs if respect_case else lc_glyphs + lc_glyphs.upper()
        pattern = fr"^[{search_glyphs}]+\s+\d+$"
    else:
        pattern = r"^\p{Ll}+\s+\d+$" if respect_case else r"^.+\s+\d+$"
    lines = regex.findall(regex.compile(pattern, regex.MULTILINE), wc_str)
    return [(l.split()[0].lower(), int(l.split()[1])) for l in lines]


def filter_cap(wc_str: str, glyphs: str, respect_case: bool) -> list[tuple[str, int]]:
    """
    Match words that are capitalized (or can be capitalized) and can be spelled with glyphs
    """
    if glyphs:
        lc_glyphs = "".join([c for c in glyphs if c.islower()])
        uc_glyphs = "".join([c for c in glyphs if c.isupper()])

        if not lc_glyphs or not uc_glyphs:
            return []

        search_glyphs = lc_glyphs if respect_case else lc_glyphs + lc_glyphs.upper()
        pattern = fr"^[{uc_glyphs + uc_glyphs.lower()}][{search_glyphs}]*\s+\d+$"
    else:
        pattern = r"^.\p{Ll}*\s+\d+$" if respect_case else r"^.+\s+\d+$"
    lines = regex.findall(regex.compile(pattern, regex.MULTILINE), wc_str)
    return [(l.split()[0].capitalize(), int(l.split()[1])) for l in lines]


def filter_caseless(wc_str: str, glyphs: str) -> list[tuple[str, int]]:
    """
    Match words that can be spelled with glyphs
    """
    if glyphs:
        # match only words that can be spelled with glyphs
        pattern = fr"^[{glyphs}]+\s+\d+$"
        lines = regex.findall(regex.compile(pattern, regex.MULTILINE), wc_str)

        return [(l.split()[0], int(l.split()[1])) for l in lines]
    else:
        # match everything
        return [(l.split()[0], int(l.split()[1])) for l in wc_str.splitlines()]


def regex_filter(wc_list: list[tuple[str, int]], regexp: str) -> list[tuple[str, int]]:
    """
    Filter words using a regular expression.
    """
    pattern = regex.compile(r"^" + regexp + r"\s+\d+$", regex.MULTILINE)
    wc_str = "\n".join(f"{w}\t{c}" for w, c in wc_list)
    lines = regex.findall(pattern, wc_str)

    return [(l.split()[0], int(l.split()[1])) for l in lines]
