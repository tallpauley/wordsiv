from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# range of rnd_punc is from 0 (default, 100% probability) to 1 (100% random)
wsv.para(rnd_punc=0.5)
