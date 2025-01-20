from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# multiple words
print(wsv.words())

# 5 words
print(wsv.words(n_words=5))

# 3-10 words
print(wsv.words(min_n_words=3, max_n_words=10))

# 10 numbers
print(wsv.words(numbers=1, n_words=10))

# 50% words, 50% numbers
print(wsv.words(numbers=0.5, n_words=10))
