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

    lang_key = language if language in punc_probabilities else "default"
    punc_dict = punc_probabilities[lang_key]

    if not punc_func:
        punc_func = default_punc_func

    start = random_available(punc_dict["start"], glyphs_string, rand)
    end = random_available(punc_dict["end"], glyphs_string, rand)
    inner = random_available(punc_dict["inner"], glyphs_string, rand)
    wrap = random_available(punc_dict["wrap"], glyphs_string, rand)

    return punc_func(words, rand, start, end, inner, wrap)


punc_probabilities = {
    "default": {
        "start": {"": 100},
        # make no ending punctuation extremely low probability so
        # it only happens when period is not available
        "end": {"": 0.00001, ".": 100, "?": 40, "!": 20},
        "inner": {"": 100, ",": 60, "—": 40, ":": 30, ";": 20},
        "wrap": {("", ""): 100, ("“", "”"): 9, ("‘", "’"): 6},
    }
}
