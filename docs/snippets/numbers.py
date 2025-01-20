from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

# No numbers (default is 0 anyway)
print(wsv.sent(numbers=0))

# 25% chance each word is a number (will make up roughly 25% of text)
print(wsv.text(numbers=0.25))

# A list of numbers
print(wsv.words(numbers=1))
