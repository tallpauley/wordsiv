from wordsiv import Vocab, WordSiv

# Make example Vocab w/ no probabilities
example_words = "grape\nApril\nBART\nDDoS"
vocab = Vocab(bicameral=True, lang="en", data=example_words)

# Build our WordSiv object
wsv = WordSiv(add_default_vocabs=False)
wsv.add_vocab("example", vocab)
wsv.vocab = "example"

# Select words that *already have* desired case in the Vocab
assert wsv.top_word(case="lc") == "grape"
assert wsv.top_word(case="cap_og") == "April"
assert wsv.top_word(case="uc_og") == "BART"
assert wsv.top_words(case="any_og") == ["grape", "April", "BART", "DDoS"]

# Select words that *can be transformed* to desired case
assert wsv.top_words(case="cap") == ["Grape", "April"]
assert wsv.top_words(case="uc") == ["GRAPE", "APRIL", "BART"]

# Select all words and transform to desired case
assert wsv.top_words(case="cap_force") == ["Grape", "April", "Bart", "Ddos"]
assert wsv.top_words(case="uc_force") == ["GRAPE", "APRIL", "BART", "DDOS"]

# Special 'any' case tries 'any_og', then tries 'cap' and 'uc' if no results
# Notice we left out the 'case' parameter on the second call, since 'any' is the default
assert wsv.top_word(glyphs="Grape", case="any") == "Grape"
assert wsv.top_word(glyphs="APRIL") == "APRIL"
