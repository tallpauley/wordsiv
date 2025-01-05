from wordsiv import WordSiv

wsv = WordSiv(vocab="en")
wsv.default_glyphs = "HAMBUGERFONTSIVhambugerfontsiv.,"

print(wsv.sent(rnd=0.03))  # rnd lets us turn up the randomness
