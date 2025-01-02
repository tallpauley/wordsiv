from wordsiv import set_vocab, set_glyphs, words, top_words

set_vocab("en")
set_glyphs("HAMBUGERFONTSIVhambugerfontsiv.,")

# Random words in Spanish containing 'ña'
words(vocab="es", glyphs="hambugerfontsivñ", n_words=5, rnd=1, contains="ña")

# Most common words in Arabic with glyphs
top_words(vocab="ar", n_words=5, min_wl=3, glyphs="خشطغب")
