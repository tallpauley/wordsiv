from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Get most common word
print(wsv.top_word())

# Get 5th most common word
print(wsv.top_word(idx=4))

# Get 5th most common word after word filters
print(wsv.top_word(idx=4, glyphs="HAMBUGERFONTSIVhambugerfontsiv", wl=7))
