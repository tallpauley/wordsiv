from random import Random


def random_available(option_weight, glyphs: str, rand, punc_temp: float | int):
    options, weights = zip(
        *{
            cs: prob ** (1 / punc_temp)
            for cs, prob in option_weight.items()
            if not glyphs or all(c in glyphs for c in cs)
        }.items()
    )
    return rand.choices(options, weights=weights, k=1)[0]


def punctuate(
    punctuation: dict,
    rand: Random,
    words: list[str],
    glyphs: str,
    punc_temp: float | int,
):
    """Punctuate a list of words and join into a sentence using punc_func"""

    start = random_available(punctuation["start"], glyphs, rand, punc_temp)
    end = random_available(punctuation["end"], glyphs, rand, punc_temp)
    inner = random_available(punctuation["inner"], glyphs, rand, punc_temp)
    wrap = random_available(punctuation["wrap"], glyphs, rand, punc_temp)

    if len(words) > 2:
        insert_index = rand.randrange(len(words) - 1)
        words[insert_index] = words[insert_index] + inner

    # place surrounding punctuation
    return wrap[0] + start + " ".join(words) + end + wrap[1]
