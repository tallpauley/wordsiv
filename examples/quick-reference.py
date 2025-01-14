from wordsiv import WordSiv

# initialize WordSiv, using Vocab "en" (English), and restricting glyphs to MY_GLYPHS
# setting the optional seed means our output will be reproducible
MY_GLYPHS = "HAMBUGERFONTSIVhambugerfontsiv.,"
wsv = WordSiv(vocab="en", glyphs=MY_GLYPHS, seed=123)

# See what other vocabs are available:
print(wsv.list_vocabs())

# Sample any word using probabilities:
print(wsv.word())

# Sample a totally random word that starts with "B", contains "a", ends with "rs"
print(wsv.word(rnd=1, startswith="B", inner="a", endswith="rs"))

# Most common word which has an inner "aa" (not overlapping first or last letter) and
# at least 6 letters
print(wsv.top_word(inner="aa", min_wl=6))

# A list of 7 totally random all caps words (including lowercase, capitalized words made
# all caps) that are 7 letters long
print(wsv.words(n_words=7, wl=7, rnd=1, case="uc"))

# Sample 5 totally random all caps words from the Vocab which are already all caps
# (useful for getting acronyms and similar)
print(wsv.words(n_words=5, rnd=1, case="uc_og"))

# List of top 5 lowercase words which are at least 15 letters long
print(wsv.top_words(n_words=5, min_wl=15, case="lc"))

# Top 5 Spanish words of 5 or less letters, which have an inner "í", made capitalized
ES_GLYPHS = "HAMBUGERFONTSIVhambugerfontsiv.,éáí"
print(
    wsv.top_words(
        vocab="es", glyphs=ES_GLYPHS, inner="í", n_words=5, max_wl=5, case="cap"
    )
)

print(wsv.top_words(n_words=5, startswith="sh", regexp=r"(?!.*[aot].*).*"))

# A sentence from word probabilities, adding a little bit of randomness
print(wsv.sent(rnd=0.03))

# A sentence in arabic with 7-10 words, drawing from only the top 100 words in the Vocab
# We are choosing not to restrict the glyphs on this WordSiv instance!
wsv_ar = WordSiv(vocab="ar", seed=123)
print(wsv_ar.sent(min_n_words=7, max_n_words=10, top_k=100))

# A sentence that isn't capitalized
print(wsv.sent(cap_first=False))

# A list of 3 sentences, with 20% chance of random figures:
print(wsv.sents(glyphs=MY_GLYPHS + "0123456789", n_sents=3, numbers=0.2))

# A paragraph:
print(wsv.para())

# A paragraph w/ no punctuation:
print(wsv.para(punc=False))

# A paragraph w/ totally random punctuation (not based on probabilities):
print(wsv.para(glyphs=MY_GLYPHS + "!?;()-–—“”‘’", rnd_punc=1))

# A paragraph in Farsi with 2-3 sentences:
print(
    wsv.para(
        vocab="fa",
        glyphs=".،أبتثجحخدذرزسشصضطظعغفقكلمنهوي",
        min_n_sents=2,
        max_n_sents=3,
    )
)

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
        numbers=0.1,
        rnd=0.1,
        rnd_punc=0.5,
        min_n_words=3,
        max_n_words=5,
        min_n_sents=2,
        max_n_sents=3,
        n_paras=3,
        para_sep="¶",
    )
)
