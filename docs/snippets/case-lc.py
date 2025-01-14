from wordsiv import WordSiv

wsv = WordSiv(vocab="en", glyphs="HAMBUGERShambugers")

print(wsv.top_word(case="lc"))
