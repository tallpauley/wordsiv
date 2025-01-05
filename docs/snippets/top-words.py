from wordsiv import WordSiv

wsv = WordSiv(vocab="en", glyphs="HAMBUGERFONTSIVhambugerfontsiv")

wsv.top_word()
# returns: 'the'

wsv.top_words()
# returns: ['the', 'of', 'to', 'in', 'for', 'is', 'on', 'that', 'this', 'it']
