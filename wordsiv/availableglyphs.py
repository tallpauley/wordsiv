import string
import unicodedata
from functools import lru_cache
from .utilities import all_utf8
import unicodedata


class AvailableGlyphs:
    def __init__(self, limit_glyphs=None):
        # all UTF8 is extremely costly to check when filtering
        # so we have self.limited to allow the filters bypass checking
        # if all characters are available
        self.limited = True if limit_glyphs else False
        self.glyphs_set = set(limit_glyphs) if limit_glyphs else all_utf8()

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def glyphs_tuple(self):
        return tuple(self.glyphs_set)

    def lowercase(self):
        return self.glyphs_in_category("Ll")

    def lc(self):
        return self.lowercase()

    def uppercase(self):
        return self.glyphs_in_category("Lu")

    def letters(self):
        return self.lowercase() + self.uppercase()

    def uc(self):
        return self.uppercase()

    def punct(self):
        return self.glyphs_in_category_starting_with("P")

    def glyphs_in_category(self, category):
        return "".join(
            c for c in self.glyphs_set if unicodedata.category(c) == category
        )

    def glyphs_in_category_starting_with(self, category_prefix):
        return "".join(
            c
            for c in self.glyphs_set
            if unicodedata.category(c).startswith(category_prefix)
        )

    def ascii_lowercase(self):
        return "".join(c for c in string.ascii_lowercase if c in self.glyphs_set)

    def ascii_uppercase(self):
        return "".join(c for c in string.ascii_uppercase if c in self.glyphs_set)

    def ascii_letters(self):
        return self.ascii_uppercase() + self.ascii_lowercase()

    def ascii_printable(self):
        return "".join(c for c in string.printable if c in self.glyphs_set)

    @lru_cache(maxsize=None)
    def have_glyphs(self, word):
        if self.limited:
            return all(char in self.glyphs_set for char in word)
        else:
            return True
