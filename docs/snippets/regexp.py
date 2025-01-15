from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

print(wsv.top_word(regexp=r"h.+b.*ger"))

# WordSiv uses regex (third-party) regex library from PyPi,
# so you can specify Unicode blocks like this:
wsv_es = WordSiv(vocab="es")
print(wsv_es.top_words(regexp=r".*\p{InLatin-1_Supplement}.*"))

# See https://www.regular-expressions.info/unicode.html for
# more examples of \p{...} syntax
