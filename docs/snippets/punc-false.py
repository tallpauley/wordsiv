from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# No punctuation
print(wsv.para(punc=False))
