from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# contains single glyph
print(wsv.top_word(endswith="s"))
# contains string
print(wsv.top_word(endswith="ats"))
