from wordsiv import WordSiv
import logging

# Initially we'll set the logger to show WARNING and more severe
log = logging.getLogger("wordsiv")
log.setLevel(logging.WARNING)

wsv = WordSiv(vocab="en")

# We see a warning in our console
print(wsv.top_word(contains="BLAH"))

# We can suppress these warnings by setting the logging level to ERROR:
log = logging.getLogger("wordsiv")
log.setLevel(logging.ERROR)

# No warning this time!
print(wsv.top_word(contains="NOWAY"))
