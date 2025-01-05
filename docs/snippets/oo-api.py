from wordsiv import WordSiv

# This sets vocab and glyphs defaults like set_vocab(), wsv.glyphs=, at object initialization
wsv_en = WordSiv(vocab="en", glyphs="hambugers")
wsv_fa = WordSiv(vocab="fa", glyphs="قنحثزعظلفع")

print(wsv_en.sent())
print(wsv_fa.sent())
