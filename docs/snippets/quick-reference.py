from wordsiv import WordSiv

MY_GLYPHS = "HAMBUGERFONTSIVhambugerfontsiv.,"
wsv = WordSiv(vocab="en", glyphs=MY_GLYPHS)

###################################################################
#################### WORD GENERATION FUNCTIONS ####################

# Word from probabilities (seed w/ MY_GLYPHS so proof stays the same):
print(wsv.word(seed=MY_GLYPHS))

# Totally random word:
print(wsv.word(rnd=1))

# Most common word (that can be spelled w/ glyphs):
print(wsv.top_word())

# 5th most common word (that can be spelled w/ glyphs):
print(wsv.top_word(idx=4))  # works like list indeces, starts at 0

# A list of words from probabilities:
print(wsv.words())

# A list of totally random words:
print(wsv.words(rnd=1))

# Most common 5 words (that can be spelled w/ glyphs):
print(wsv.top_words(n_words=5))

# A sentence:
print(wsv.sent())

# 3 sentences:
print(wsv.sents(n_sents=3))

# A paragraph:
print(wsv.para())

# A list of 2 Paragraphs:
print(wsv.paras(n_paras=2))

# Block of text:
print(wsv.text())

###################################################################
#################### LETTER CASE OPTIONS ##########################

# The default is `case='any'`, which transforms the case if not getting results:
# - try to get (unmodified) words from Vocab which can be spelled with "ZO" and have at
#   least 5 characters: No results.
# - try to capitalize Vocab words: "zoo" becomes "Zoo" but we can't spell it without
#   'o'. No results.
# - try to uppercase Vocab words: "zoo" becomes "ZOO", Bingo! Returns 'ZOO' as most
#   common word!
print(wsv.top_word(glyphs="ZO", min_wl=3))

# Same as above. `any` is the default if case isn't specified:
print(wsv.top_word(glyphs="ZO", case="any", min_wl=3))

# `case='any_og'` doesn't try to apply case transformations. So we get no results.
print(wsv.top_word(glyphs="ZO", min_wl=3, case="any_og"))

# Lowercase words, includes only words that are lowercase in the Vocab:
# - No case transforms happen by default, since we wouldn't want to transform words like
#  'Paris', 'FAA', or 'DDoS' to lowercase
print(wsv.top_words(case="lc", n_words=5))

# Capitalized words, includes:
# - words that are capitalized in the Vocab
# - words that are lowercase in the Vocab, transformed to capitalized
print(wsv.top_words(case="cap", n_words=5))

# All-caps words, includes:
# - words that are all-caps in the Vocab
# - words that are capitalized in the Vocab, transformed to all-caps
# - words that are lowercase in the Vocab, transformed to all-caps
print(wsv.top_words(case="uc", n_words=5))

# Words that are capitalized in the Vocab:
print(wsv.top_words(case="cap_og", n_words=5))

# Words that are all-caps in the Vocab:
print(wsv.top_words(case="uc_og", n_words=5))

# Transform ANY word to lowercase (even capitalized, all-caps, and camel-case words!):
print(wsv.top_words(case="lc_force", n_words=5))

# Transform ANY word to capitalized (even all-caps and camel-case words!)
print(wsv.top_words(case="cap_force", n_words=5))


###################################################################
#################### WORD FILTER OPTIONS ##########################

# These options can be used on ALL word generation functions, from `word()` all the way
# up to `text()`. Here they are demonstrated w/ top_word for simplicity:

# Exact word length:
print(wsv.top_word(wl=7))

# Word length min, max
print(wsv.top_word(min_wl=8, max_wl=12))

# Word starts with a glyph
print(wsv.top_word(startswith="v"))

# Word starts with a string
print(wsv.top_word(startswith="ev"))

# Word ends with a glyph
print(wsv.top_word(endswith="s"))

# Word ends with a string
print(wsv.top_word(endswith="ts"))

# Contains a glyph
print(wsv.top_word(contains="a"))

# Contains a string
print(wsv.top_word(contains="rr"))

# Contains multiple strings, glyphs
# (Note: list doesn't work, uses tuple for caching)
print(wsv.top_word(contains=("b", "rr")))

# Has character "inside" (in substring of word excluding first and last glyph)
print(wsv.top_word(inner="b"))

# Has string "inside" (in substring of word excluding first and last glyph)
print(wsv.top_word(inner="br"))

# Has multiple strings "inside" (in substring of word excluding first and last glyph)
# (Note: list doesn't work, uses tuple for caching)
print(wsv.top_word(inner=("br", "ck")))

# Word matches Regular Expression
print(wsv.top_word(regexp=r"h.+b.*ger"))

# WordSiv uses regex (third-party) regex library from PyPi, so you can specify Unicode
# blocks like this:
wsv_es = WordSiv(vocab="es")
print(wsv_es.top_word(regexp=r".*\p{InLatin-1_Supplement}.*"))

# See https://www.regular-expressions.info/unicode.html for more ways you can use this
# library to match Unicode blocks.


# Random words in Spanish containing 'ña':
print(wsv.words(vocab="es", glyphs="hambugerfontsivñ", n_words=5, rnd=1, contains="ña"))

# Most common words in Arabic with glyphs 'خشطغب':
print(wsv.top_words(vocab="ar", n_words=5, min_wl=3, glyphs="خشطغب"))
