from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Top 100 most frequent words
print(wsv.text(top_k=100))

# This is useful to get a selection of highly-frequent words, without skewing towards
# the top few words.
print(wsv.text(rnd=1, top_k=1000))
