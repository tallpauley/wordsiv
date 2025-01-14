from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# We don't get any words, because there are no words of at least 5 letters in our Vocab
# that "AIPRS" can spell w/out converting to uppercase.
print(wsv.top_word(glyphs="AIPRS", case="any_og", min_wl=5))
