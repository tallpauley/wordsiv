from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# random single word from probabilities
print(wsv.word())

# random single word with glyphs restriction
print(wsv.word(glyphs="HAMBUGERFONTSIVhambugerfontsiv"))

# random single word, no probablities
print(wsv.word(rnd=1))
