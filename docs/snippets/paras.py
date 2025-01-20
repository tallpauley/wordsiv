from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Random number of paragraphs
print(wsv.paras())

# 3 paragraphs
print(wsv.paras(n_paras=3))
