from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Contains glyph inside (word[1:-1])
print(wsv.top_word(inner="b"))
# Contains string inside (word[1:-1])
print(wsv.top_word(inner="br"))

# Contains multiple strings inside (word[1:-1])
# `inner` only accepts a tuple, not a list (this is for caching)
print(wsv.top_word(inner=("br", "ck")))
