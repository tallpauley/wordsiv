from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Default behavior - based on punctuation probabilities
print(wsv.sent(rnd_punc=0))

# Completely random punctuation selection
print(wsv.sent(rnd_punc=1))

# Interpolation between totally random punc selection and probability-based punc
# selection
print(wsv.sent(rnd_punc=0.5))
