from wordsiv import set_vocab, para

set_vocab("en")

# paragraph in English
print(para())
# paragraph in Spanish
print(para(vocab="es"))
