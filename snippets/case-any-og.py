from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# We don't get any words, because there are no words of at least 5 letters in
# our Vocab that "AIPRS" can spell
print(wsv.top_word(glyphs="AIPRS", case="any_og", min_wl=5))

# However, this returns "Paris" since we have all the glyphs
print(wsv.top_word(glyphs="aiPrs", case="any_og", min_wl=5))
