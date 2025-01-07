from __future__ import annotations

import random

DEFAULT_PUNCTUATION = {
    "en": {
        "insert": {
            " ": 0.365,
            ", ": 0.403,
            ": ": 0.088,
            "; ": 0.058,
            "–": 0.057,
            "—": 0.022,
            " … ": 0.006,
        },
        "wrap_sent": {
            ("", "."): 0.923,
            ("", "!"): 0.034,
            ("", "?"): 0.04,
            ("", "…"): 0.003,
        },
        "wrap_inner": {
            ("", ""): 0.825,
            ("(", ")"): 0.133,
            ("‘", "’"): 0.013,
            ("“", "”"): 0.028,
        },
    },
    "ar": {
        "insert": {" ": 0.364, ": ": 0.108, "، ": 0.463, "؛ ": 0.066},
        "wrap_sent": {("", "."): 0.914, ("", "؟"): 0.052, ("", "!"): 0.033},
        "wrap_inner": {("", ""): 0.971, ("’", "‘"): 0.007, ("”", "“"): 0.022},
    },
    "fa": {
        "insert": {" ": 0.364, ": ": 0.108, "، ": 0.463, "؛ ": 0.066},
        "wrap_sent": {("", "."): 0.914, ("", "؟"): 0.052, ("", "!"): 0.033},
        "wrap_inner": {("", ""): 0.971, ("’", "‘"): 0.007, ("”", "“"): 0.022},
    },
    "es": {
        "insert": {
            " ": 0.277,
            ", ": 0.49,
            ": ": 0.093,
            "; ": 0.073,
            "– ": 0.026,
            "— ": 0.03,
            "… ": 0.011,
        },
        "wrap_sent": {
            ("", "."): 0.928,
            ("¡", "!"): 0.029,
            ("¿", "?"): 0.036,
            ("", "…"): 0.008,
        },
        "wrap_inner": {
            ("", ""): 0.814,
            ("(", ")"): 0.129,
            ("‘", "’"): 0.013,
            ("“", "”"): 0.044,
        },
    },
}


def _random_available(option_weight, glyphs: str | None, rand, rnd_punc: float):
    punc_prob = {
        (punc, (1 - rnd_punc) * prob + rnd_punc * 1)
        for punc, prob in option_weight.items()
        # if glyphs is set, check if we have the glyphs we need to punctuate
        # we aren't strict about having spaces, hence glyphs + ' '
        if not glyphs or all(c in glyphs + " " for c in punc)
    }

    if punc_prob:
        options, weights = zip(*punc_prob)
        return rand.choices(options, weights=weights, k=1)[0]
    else:
        return None


def _punctuate(
    punctuation: dict,
    rand: random.Random,
    words: list[str],
    glyphs: str | None,
    rnd_punc: float,
):
    """Punctuate a list of words and join into a sentence using a punctuation dict"""

    insert = _random_available(punctuation["insert"], glyphs, rand, rnd_punc) or ""
    wrap_sent = _random_available(punctuation["wrap_sent"], glyphs, rand, rnd_punc) or (
        "",
        "",
    )
    wrap_inner = _random_available(
        punctuation["wrap_inner"], glyphs, rand, rnd_punc
    ) or ("", "")

    if len(words) > 2:
        # place inner wrap punctuation on words (parentheses, quotes, etc)
        wrap_left_index = rand.randrange(0, len(words) - 1)
        wrap_right_index = rand.randrange(wrap_left_index, len(words) - 1)
        words[wrap_left_index] = wrap_inner[0] + words[wrap_left_index]
        words[wrap_right_index] = words[wrap_right_index] + wrap_inner[1]

        # add insert punctuation and spaces
        # pick an index that hasn't already been used (simpler)
        insert_index = rand.choice(
            [
                n
                for n in range(1, len(words) - 1)
                if n not in [words[wrap_left_index], words[wrap_right_index]]
            ]
        )

        # put "insert" punctuation in place of a space
        separators = [" "] * (len(words) - 1)
        separators[insert_index - 1] = insert
        sent = "".join(
            [t for pair in zip(words, separators) for t in pair] + [words[-1]]
        )
    else:
        sent = " ".join(words)

    # place surrounding punctuation
    return wrap_sent[0] + sent + wrap_sent[1]
