from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Text block w/ random number of paragraphs
print(wsv.text())

# Text block with special paragraph separator
print(wsv.text(para_sep="¶"))

# Text block w/ 3 paragraphs
print(wsv.text(n_paras=3))
