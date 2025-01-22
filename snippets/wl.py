from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Exactly 7 letters
print(wsv.top_word(wl=7))

# At least 4 letters
print(wsv.top_word(min_wl=4))

# No more than 20 letters
print(wsv.top_word(max_wl=20))

# At least 10 letters, no more than 20 letters
print(wsv.top_word(min_wl=10, max_wl=20))
