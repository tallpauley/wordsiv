from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# contains single glyph
print(wsv.top_word(contains="a"))
# contains string
print(wsv.top_word(contains="orr"))

# contains multiple glyphs/strings
# `inner` only accepts a tuple, not a list (this is for caching)
print(wsv.top_word(contains=("b", "rr")))
