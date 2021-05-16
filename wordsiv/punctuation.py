def default_punc_func(words, rand, start, end, inner, wrap):
    # Sort of derived from wikipedia, but increased freq of lesser used punctuation
    # https://en.wikipedia.org/wiki/English_punctuation#Frequency

    # place "inner" punctuation (like comma, hyphen, etc)
    insert_index = rand.randrange(len(words) - 1)
    words[insert_index] = words[insert_index] + inner

    # place surrounding punctuation
    return wrap[0] + start + " ".join(words) + end + wrap[1]


def random_available(option_weight, glyphs_string, rand):
    options, weights = zip(
        *{
            cs: prob
            for cs, prob in option_weight.items()
            if all(c in glyphs_string for c in cs)
        }.items()
    )
    return rand.choices(options, weights=weights, k=1)[0]


def punctuate(words, glyphs_string, rand, language, punc_func=None):
    """Punctuate a list of words and join into a sentence using punc_func

    Example w/ no punc available:
    >>> import random
    >>> words = ["hamburger", "fonts", "vise", "gurb", "ram"]
    >>> glyphs_string = 'HAMBURGERFONTSIVhamburgerfontsiv'
    >>> rand = random.Random(5)
    >>> punctuate(words, glyphs_string, rand, "en", default_punc_func)
    'hamburger fonts vise gurb ram'

    Example w/ punc available:
    >>> glyphs_string = 'HAMBURGERFONTSIVhamburgerfontsiv.,'
    >>> punctuate(words, glyphs_string, rand, "en", default_punc_func)
    'hamburger fonts vise gurb ram.'

    """

    if not punc_func:
        punc_func = default_punc_func

    start = random_available(
        default_punctuation[language]["start"], glyphs_string, rand
    )
    end = random_available(default_punctuation[language]["end"], glyphs_string, rand)
    inner = random_available(
        default_punctuation[language]["inner"], glyphs_string, rand
    )
    wrap = random_available(default_punctuation[language]["wrap"], glyphs_string, rand)

    return punc_func(words, rand, start, end, inner, wrap)


default_punctuation = {
    "en": {
        "start": {"": 10},
        # make no ending punctuation extremely low probability so
        # it only happens when period is not available
        "end": {"": 0.00001, ".": 10, "?": 4, "!": 2},
        "inner": {"": 10, ",": 6, "—": 4, ":": 3, ";": 2},
        "wrap": {("", ""): 10, ("“", "”"): 2},
    }
}
