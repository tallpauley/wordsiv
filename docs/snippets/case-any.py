from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# The word appears as "Paris" in the vocab, but since we're using (the default)
# case='any', we get the capitalized word.
print(wsv.top_word(glyphs="AIPRS", min_wl=5))
