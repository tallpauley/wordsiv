from wordsiv import WordSiv

wsv = WordSiv(vocab="en", glyphs="HAMBUGERFONTSIVhambugerfontsiv")

# Default behavior - based on word frequencies
print(wsv.words(n_words=10))

# Completely random selection
print(wsv.words(n_words=10, rnd=1))

# Blending in just a little bit of randomness helps when you have a very constricted
# glyphs set like "HAMBUGERFONTS"
print(wsv.words(n_words=10, rnd=0.03))
