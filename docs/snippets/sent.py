from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Sentence of random length
print(wsv.sent())

# Sentence w/ no punctuation
print(wsv.sent(punc=False))

# Sentence w/ 5 words and completely random punctuation
print(wsv.sent(rnd_punc=1, n_words=5))

# Sentence w/ 3-10 words
print(wsv.sent(min_n_words=3, max_n_words=10))

# String of 10 numbers
print(wsv.sent(numbers=1, n_words=10))

# 50% words, 50% numbers
print(wsv.words(numbers=0.5, n_words=10))
