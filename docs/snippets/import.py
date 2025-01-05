from wordsiv import WordSiv

# Make a WordSiv object, w/ default Vocab set to English
wsv = WordSiv(vocab="en")

# Generate a sentence w/out any word filtering
print(wsv.sent())
