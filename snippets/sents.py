from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# A random number of sentences
print(wsv.sents())

# 5 sentences
print(wsv.sents(n_sents=5))

# 2-3 sentences
print(wsv.sents(min_n_sents=2, max_n_sents=3))
