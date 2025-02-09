from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Get 10 most common words
print(wsv.top_words(n_words=10))

# Get the 10th-19th most common words
print(wsv.top_words(n_words=10, idx=9))

# Get 10 most common words after word filters
print(wsv.top_words(n_words=10, glyphs="HAMBUGERFONTSIVhambugerfontsiv", wl=7))
