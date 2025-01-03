import wordsiv

# This sets vocab and glyphs defaults like set_vocab(), set_glyphs(), at object initialization
wsv_en = wordsiv.WordSiv(vocab="en", glyphs="hambugers")
wsv_fa = wordsiv.WordSiv(vocab="fa", glyphs="قنحثزعظلفع")

print(wsv_en.sent())
print(wsv_fa.sent())
