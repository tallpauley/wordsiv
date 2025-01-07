from wordsiv import WordSiv, FilterError
import logging

########################################################################################
############################# SETUP WORDSIV ############################################

# Initialize WordSiv object with default vocab and glyphs:
MY_GLYPHS = "HAMBUGERFONTSIVhambugerfontsiv.,"
wsv = WordSiv(vocab="en", glyphs=MY_GLYPHS)

# We can also set the default glyphs and vocab after our WordSiv object is initialized:
# Exactly the same settings as above, so this changes nothing:
wsv.default_glyphs = MY_GLYPHS
wsv.default_vocab = "en"

# Use `list_vocabs()` to see Vocabs are available:
print(wsv.list_vocabs())

# We recommend seeding the WordSiv with our glyphs, so your output only changes when
# your glyphs or your script change:
wsv.seed(MY_GLYPHS)


########################################################################################
######################### WORD GENERATION FUNCTIONS ####################################

# Word from probabilities
print(wsv.word())

# Totally random word:
print(wsv.word(rnd=1))

# Most common word (that can be spelled w/ glyphs):
print(wsv.top_word())

# 5th most common word (that can be spelled w/ glyphs):
# - works like list indeces, starts at 0
print(wsv.top_word(idx=4))

# A list of words from probabilities:
print(wsv.words())

# A list of totally random words:
print(wsv.words(rnd=1))

# A list of 15 words:
print(wsv.words(n_words=15))

# List of words from probabilities, only pick from top 100 words (after filtering)
print(wsv.words(top_k=100))

# A list of 10-20 words:
print(wsv.words(min_n_words=10, max_n_words=20))

# List of five most-common words (that can be spelled w/ glyphs):
print(wsv.top_words(n_words=5))

# A sentence:
print(wsv.sent())

# A sentence w/out asking for a capitalized first word:
print(wsv.sent(cap_first=False))

# A list of 3 sentences, with 20% chance of random figures:
print(wsv.sents(glyphs=MY_GLYPHS + "0123456789", n_sents=3, numbers=0.2))

# A paragraph:
print(wsv.para())

# A paragraph w/ no punctuation:
print(wsv.para(punc=False))

# A paragraph w/ totally random punctuation (not based on probabilities):
print(wsv.para(glyphs=MY_GLYPHS + "!?;()-–—“”‘’", rnd_punc=1))

# A paragraph with 2-3 sentences:
print(wsv.para(min_n_sents=2, max_n_sents=3))

# A list of 2 Paragraphs:
print(wsv.paras(n_paras=2))

# Block of text:
print(wsv.text())

# Block of text w/
# - 3 paragraphs, 2-3 sentences a paragraph, 3-5 words a sentence
# - paragraphs separated by "¶":
# - roughly 10% figures, 10% chance of random words
# - 50% totally random punctuation distribution
print(
    wsv.text(
        glyphs=MY_GLYPHS + "0123¶-–—“”‘’();!?",
        n_paras=3,
        numbers=0.1,
        min_n_sents=2,
        max_n_sents=3,
        min_n_words=3,
        max_n_words=5,
        rnd=0.1,
        rnd_punc=0.5,
        para_sep="¶",
    )
)

###########################################################################
######################### LETTER CASE OPTIONS #############################

# The default is `case='any'`, which progressively transforms the case to expand results
# if all words are being filtered out:
# - try to get (unmodified) words from Vocab which can be spelled with "ZO" (that have
#   at least 3 characters): No results.
# - try to capitalize Vocab words: "zoo" becomes "Zoo" but we can't spell it without
#   'o'. No results.
# - try to uppercase Vocab words: "zoo" becomes "ZOO", Bingo! Returns 'ZOO' as most
#   common word!
print(wsv.top_word(glyphs="ZO", min_wl=3))

# Same result as preceding example. `any` is the default if `case` isn't specified:
print(wsv.top_word(glyphs="ZO", case="any", min_wl=3))

# `case='any_og'` doesn't progressively apply case transformations. We get no results.
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

# Words that are capitalized in the Vocab (useful for proper nouns, etc.):
print(wsv.top_words(case="cap_og", n_words=5))

# Words that are all-caps in the Vocab (useful for acronyms):
print(wsv.top_words(case="uc_og", n_words=5))

# Transform ANY word to lowercase (even capitalized, all-caps, and camel-case words!):
print(wsv.top_words(case="lc_force", n_words=5))

# Transform ANY word to capitalized (even all-caps and camel-case words!)
print(wsv.top_words(case="cap_force", n_words=5))

###########################################################################
######################### WORD FILTER OPTIONS #############################

# These options can be used on ALL word generation functions, from `word()` all the way
# up to `text()`. Here they are demonstrated w/ top_word, top_words for simplicity:

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
print(wsv.top_word(endswith="ats"))

# Contains a glyph
print(wsv.top_word(contains="a"))

# Contains a string
print(wsv.top_word(contains="orr"))

# Contains multiple strings, glyphs
# (Note: only accepts a tuple, not a list — this is for caching)
print(wsv.top_word(contains=("b", "rr")))

# Has character "inside" (substring of word excluding first, last glyph)
print(wsv.top_word(inner="b"))

# Has string "inside" (substring of word excluding first, last glyph)
print(wsv.top_word(inner="br"))

# Has multiple strings "inside" (in substring of word excluding first and last glyph)
# (Note: only accepts a tuple, not a list — this is for caching)
print(wsv.top_word(inner=("br", "ck")))

# Word matches Regular Expression
print(wsv.top_word(regexp=r"h.+b.*ger"))

# WordSiv uses regex (third-party) regex library from PyPi, so you can specify Unicode
# blocks like this:
wsv_es = WordSiv(vocab="es")
print(wsv_es.top_words(regexp=r".*\p{InLatin-1_Supplement}.*"))

# See https://www.regular-expressions.info/unicode.html for more examples of \p{...}
# syntax

###########################################################################
########################## WORD FILTER ERRORS #############################

# WordSiv by default will log a warning to the console if it can't find any words
wsv.top_word(contains="NOWAY")

# We can suppress these warnings by setting the logging level to ERROR:
log = logging.getLogger("wordsiv")
log.setLevel(logging.ERROR)
wsv.top_word(contains="NOWAY")

# Or, we can make WordSiv raise an error if it can't find any words:
wsv.raise_errors = True
try:
    wsv.top_word(contains="NOWAY")
except FilterError as e:
    print(f'Exception "{e}" would stop our script (if we didn\'t catch it w/ `except`)')
