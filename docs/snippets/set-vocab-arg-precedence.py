from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# paragraph in English
print(wsv.para())
# paragraph in Spanish
print(wsv.para(vocab="es"))
