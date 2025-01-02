from wordsiv import set_vocab, set_glyphs, words

set_vocab("en")
set_glyphs("HAMBUGERFONTShambugerfonts.,")

# uses glyphs "HAMBUGERFONTShambugerfonts.,"
print(words(glyphs="hambugerfonts.,"))
# uses glyphs "hambugerfonts.,""
print(words(glyphs="hambugerfonts.,"))
