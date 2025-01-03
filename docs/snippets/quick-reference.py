from wordsiv import (
    set_vocab,
    set_glyphs,
    word,
    words,
    top_word,
    top_words,
    sent,
    sents,
    para,
    paras,
    txt,
)

MY_GLYPHS = "HAMBUGERFONTSIVhambugerfontsiv.,"
set_vocab("en")
set_glyphs(MY_GLYPHS)

print("######## WORD GENERATION FUNCTIONS #########\n")
print("-> Word from probabilities (seed w/ MY_GLYPHS so proof stays the same):")
print(word(seed=MY_GLYPHS))

print("-> Totally random word:")
print(word(rnd=1))

print("-> Most common word (that can be spelled w/ glyphs):")
print(top_word())

print("-> 5th most common word (that can be spelled w/ glyphs):")
print(top_word(idx=4))  # works like list indeces, starts at 0

print("-> A list of words from probabilities:")
print(words())

print("-> A list of totally random words:")
print(words(rnd=1))

print("-> Most common 5 words (that can be spelled w/ glyphs):")
print(top_words(n_words=5))

print("-> A sentence:")
print(sent())

print("-> 3 sentences:")
print(sents(n_sents=3))

print("-> A paragraph:")
print(para())

print("-> A list of 2 Paragraphs:")
print(paras(n_paras=2))

print("-> Block of text:")
print(txt())

print("\n######## LETTER CASE OPTIONS #########\n")

# TODO we need documentation and tests for this
print(
    "-> Default tries to be smart and uppercase/capitalize if it's reasonable to do so:"
)
print(top_word(glyphs="PARIS", min_wl=5))

print('-> Do NOT transform case of words from Vocab ("Paris" is capitalized in Vocab):')
print(top_word(glyphs="PARIS", min_wl=5, case="any_og"))

print("-> Lowercased Words:")
print(top_words(case="lc", n_words=5))

print("-> Capitalized Words:")
print(top_words(case="cap", n_words=5))

print("-> All Uppercase Words:")
print(top_words(case="uc", n_words=5))

print("-> Words that are capitalized in the Vocab:")
print(top_words(case="cap_og", n_words=5))

print("-> Words that are all uppercase in the Vocab:")
print(top_words(case="uc_og", n_words=5))

print("-> Transform ANY word to lowercase (even capitalized and all uppercase words!):")
print(top_words(case="lc_force", n_words=5))

print("-> Transform ANY word to capitalized (even those that should be all uppercase)")
print(top_words(case="cap_force", n_words=5))


print("-> Random words in Spanish containing 'ña':")
print(words(vocab="es", glyphs="hambugerfontsivñ", n_words=5, rnd=1, contains="ña"))

print("-> Most common words in Arabic with glyphs 'خشطغب':")
print(top_words(vocab="ar", n_words=5, min_wl=3, glyphs="خشطغب"))
