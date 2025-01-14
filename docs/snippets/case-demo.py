from wordsiv import Vocab, WordSiv

# Make a custom Vocab (just for example) w/ no probabilities
test_data = "grape\nApril\nBART\nDDoS"
vocab = Vocab(bicameral=True, lang="en", data=test_data)

# Build our WordSiv object
wsv = WordSiv(add_default_vocabs=False)
wsv.add_vocab("example", vocab)
wsv.default_vocab = "example"

# Words that already have desired case
assert wsv.top_word(case="lc") == "grape"
assert wsv.top_word(case="cap_og") == "April"
assert wsv.top_word(case="uc_og") == "BART"
assert wsv.top_words(case="any_og") == ["grape", "April", "BART", "DDoS"]

# Words that can be transformed to desired case (notice DDoS isn't capitalized)
assert wsv.top_words(case="cap") == ["Grape", "April"]
assert wsv.top_words(case="uc") == ["GRAPE", "APRIL", "BART"]

# _force options don't respect existing letter case
assert wsv.top_words(case="cap_force") == ["Grape", "April", "Bart", "Ddos"]
assert wsv.top_words(case="uc_force") == ["GRAPE", "APRIL", "BART", "DDOS"]

# Special 'any' case tries 'any_og', then tries 'cap' and 'uc' if no results
assert wsv.top_word(glyphs="Grape", case="any") == "Grape"
# we can leave out this parameter, since 'any' is the default case
assert wsv.top_word(glyphs="APRIL") == "APRIL"
