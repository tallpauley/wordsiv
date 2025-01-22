from wordsiv import WordSiv, FilterError

wsv = WordSiv(vocab="en", raise_errors=True)

try:
    wsv.top_word(contains="NOWAY")
except FilterError as e:
    print(f'We can handle our error "{e}" here!')
