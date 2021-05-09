from fontTools.pens.basePen import NullPen  # type: ignore
from fontTools.ttLib import TTFont  # type: ignore
from collections import defaultdict
from functools import lru_cache


class FontInfo:
    def __init__(self, font_file):
        # For glyphs generated files, we must check not just if glyphs are in font, but if they have data in them
        self.font_file = font_file
        self.font = TTFont(
            font_file, 0, allowVID=0, ignoreDecompileErrors=True, fontNumber=-1
        )

    # return glyph names that contain paths
    def glyphs_with_paths(self):
        glyphSet = self.font.getGlyphSet()
        glyph_names_with_paths = []

        for name in self.font.getGlyphNames():
            existsPen = self.PathExistsPen()
            glyphSet[name].draw(existsPen)
            if existsPen.exists:
                glyph_names_with_paths.append(name)

        return glyph_names_with_paths

    # return list of unicode characters that have paths
    @property  # type: ignore
    @lru_cache(maxsize=None)
    def characters(self):

        # build reverse lookup
        reverse_unicode_map = defaultdict(list)

        for k, v in self.cmap.items():
            reverse_unicode_map[v].append(k)

        chars = []
        for name in self.glyphs_with_paths():
            # use try/except to weed out glyphs that don't have a unicode mapping
            try:
                chars.append(chr(reverse_unicode_map[name][0]))
            except IndexError:
                pass

        return chars

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def cmap(self):
        return self.font.getBestCmap()

    def glyph_name(self, character):
        return self.cmap[ord(character)][0]

    # no metrics here, just width of actual glyph itself
    def char_width(self, character):
        glyph_name = self.glyph_name(character)
        glyph_set = self.font.getGlyphSet()

        return glyph_set[glyph_name].width

    @property  # type: ignore
    @lru_cache(maxsize=None)
    def char_widths(self):
        widths = {}
        for c in self.characters:
            widths[c] = self.char_width(c)

        return widths

    def char_widths_tuple(self):
        return tuple(self.char_widths.items())

    @lru_cache(maxsize=None)
    def rough_word_width(self, string):
        return sum(self.char_width(c) for c in string)

    # def word_width(self, string):
    #     drawBot.font(self.font_file, 1000)
    #     return int(drawBot.textSize(string)[0])

    ## A pen for checking if a glyph contains any path data (probably a simpler way to do this???)
    class PathExistsPen(NullPen):
        def __init__(self):
            NullPen.__init__(self)
            self.exists = False

        def lineTo(self, _):
            self.exists = True

        def curveTo(self, _, _2, _3):
            self.exists = True

        def qCurveTo(self, _, _2, _3):
            self.exists = True
