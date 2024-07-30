from random import Random


def default_punc_func(words, rand: Random, start, end, inner, wrap):

    # place "inner" punctuation (like comma, hyphen, etc)
    if len(words) > 2:
        insert_index = rand.randrange(len(words) - 1)
        words[insert_index] = words[insert_index] + inner

    # place surrounding punctuation
    return wrap[0] + start + " ".join(words) + end + wrap[1]


def random_available(option_weight, glyphs: str, rand):
    options, weights = zip(
        *{
            cs: prob
            for cs, prob in option_weight.items()
            if not glyphs or all(c in glyphs for c in cs)
        }.items()
    )
    return rand.choices(options, weights=weights, k=1)[0]


def punctuate(
    punctuation: dict, rand: Random, words: list[str], glyphs: str, punc_func=None
):
    """Punctuate a list of words and join into a sentence using punc_func"""

    if not punc_func:
        punc_func = default_punc_func

    start = random_available(punctuation["start"], glyphs, rand)
    end = random_available(punctuation["end"], glyphs, rand)
    inner = random_available(punctuation["inner"], glyphs, rand)
    wrap = random_available(punctuation["wrap"], glyphs, rand)

    return punc_func(words, rand, start, end, inner, wrap)
