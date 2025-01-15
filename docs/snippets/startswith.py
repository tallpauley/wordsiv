from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# starts with single glyph
print(wsv.top_word(startswith="v"))

# starts with string
print(wsv.top_word(startswith="ev"))
