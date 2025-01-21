from wordsiv import WordSiv

# Set seed on initialization
wsv = WordSiv(vocab="en", seed=123)
print(wsv.words(n_words=5))

# Or set seed for specific calls
wsv = WordSiv(vocab="en")
print(wsv.words(n_words=5, seed=123))
