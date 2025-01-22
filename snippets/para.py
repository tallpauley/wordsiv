from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# Paragraph w/ random number of sentences
print(wsv.para())

# Paragraph w/ 3 sentences
print(wsv.para(n_sents=3))

# Paragraph which joins sentences with a custom separator
print(wsv.para(sent_sep="\n"))

# Paragraph w/ 1-3 sentences
print(wsv.para(min_n_sents=1, max_n_sents=3))
