from wordsiv import set_model, word
from collections import defaultdict
from itertools import product
import string


def gj_proof_en(glyphs, case="cap"):

    set_model("en_prob_books")
    uc_glyphs = "".join(sorted(c for c in glyphs if c.isupper()))
    lc_glyphs = "".join(sorted(c for c in glyphs if c.islower()))

    if case == "cap":
        pairs = [f"{uc}{lc}" for uc in uc_glyphs for lc in lc_glyphs]
    elif case == "lc":
        pairs = ["".join(pair) for pair in product(lc_glyphs, repeat=2)]
    elif case == "uc":
        pairs = ["".join(pair) for pair in product(uc_glyphs, repeat=2)]
    else:
        raise ValueError(f"Invalid case: {case}")

    words = []
    for pair in pairs:
        if case == "cap":
            w = word(glyphs=glyphs, startswith=pair, case="cap", min_wl=5, idx=0)
        elif case == "lc":
            w = word(glyphs=glyphs, inner=pair, case="lc", min_wl=5, idx=0)
        elif case == "uc":
            w = word(glyphs=glyphs, inner=pair, case="uc", min_wl=5, idx=0)
        if w:
            words.append(w)

    return " ".join(words)


def gj_proof_ar(glyphs, mode):
    set_model("ar_prob_subs")
    pairs = ["".join(pair) for pair in product(glyphs, repeat=2)]

    for pair in pairs:
        if mode == "init":
            w = word(glyphs=glyphs, startswith=pair, min_wl=5, idx=0)
        if mode == "medi":
            w = word(glyphs=glyphs, inner=pair, min_wl=5, idx=0)
        if mode == "fina":
            w = word(glyphs=glyphs, endswith=pair, min_wl=5, idx=0)


if __name__ == "__main__":
    glyphs = "HAMBUGERFONTSIVhambugerfontsiv.,"
    # glyphs = string.ascii_letters

    print(gj_proof_en(glyphs, case="cap"))
    print(gj_proof_en(glyphs, case="uc"))
    print(gj_proof_en(glyphs, case="lc"))

    # glyphs = "ناتيومرلبسفأعدقحكهجشطصزخضغذثئةظؤىءآإ"
    # print(gj_proof_ar(glyphs, mode="medi"))
