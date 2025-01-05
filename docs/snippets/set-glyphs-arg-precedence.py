from wordsiv import WordSiv

wsv = WordSiv(vocab="en", glyphs="HAMBUGERFONTShambugerfonts.,")

# uses glyphs "HAMBUGERFONTShambugerfonts.,"
print(wsv.words())
# uses glyphs "hambugerfonts.,""
print(wsv.words(glyphs="hambugerfonts.,"))
