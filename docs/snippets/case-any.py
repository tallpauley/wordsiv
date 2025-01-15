from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

#   Returns 'ZOO' as most common word
print(wsv.top_word(glyphs="ZO", min_wl=5))

# No `case` arg, so the default is `case='any'` which will:
# - try to get (unmodified) words from Vocab which can be spelled with "ZO"
#   (that have at least 3 characters): No results.
# - try to capitalize Vocab words: "zoo" becomes "Zoo" but we can't spell it
#   without 'o'. No results.
# - try to uppercase Vocab words: "zoo" becomes "ZOO", which we can spell!
