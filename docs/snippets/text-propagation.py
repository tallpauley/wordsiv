from wordsiv import WordSiv

wsv = WordSiv(vocab="en")

print(
    wsv.text(
        n_paras=3,  # number of paragraphs
        min_n_sents=2,  # min sentences per paragraph
        max_n_sents=4,  # max sentences per paragraph
        min_n_words=3,  # min words per sentence
        max_n_words=7,  # max words per sentence
        numbers=0.1,  # 10% chance of numbers
        rnd=0.1,  # 10% random word selection
        rnd_punc=0.5,  # 50% random punctuation
        para_sep="¶",  # custom paragraph separator
        min_wl=5,  # minimum word length
        max_wl=10,  # maximum word length
        contains="a",  # words contains substring (doesn't affect numbers)
    )
)
