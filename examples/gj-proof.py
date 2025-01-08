"""WordSiv Proof inspired by http://www.galvanizedjets.com/"""

from wordsiv import WordSiv
from itertools import product
import logging

wsv_log = logging.getLogger("wordsiv")
wsv_log.setLevel(logging.ERROR)


def gj_proof_en(glyphs, case="cap"):
    wsv = WordSiv(vocab="en", glyphs=glyphs)

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
            w = wsv.top_word(startswith=pair, case="cap", min_wl=4)
        elif case == "lc":
            w = wsv.top_word(inner=pair, case="lc", min_wl=4)
        elif case == "uc":
            w = wsv.top_word(inner=pair, case="uc", min_wl=4)
        if w:
            words.append(w)

    return " ".join(words)


def gj_proof_ar(glyphs, mode):
    wsv = WordSiv(vocab="ar", glyphs=glyphs)

    pairs = ["".join(pair) for pair in product(glyphs, repeat=2)]

    word_list = []
    for pair in pairs:
        if mode == "init":
            w = wsv.top_word(startswith=pair, min_wl=5)
        elif mode == "medi":
            w = wsv.top_word(inner=pair, min_wl=5)
        elif mode == "fina":
            w = wsv.top_word(endswith=pair, min_wl=5)
        if w:
            word_list.append(w)

    return " ".join(word_list)


if __name__ == "__main__":
    glyphs = "HAMBUGERFONTSIVhambugerfontsiv.,"
    proof = ""
    proof = f"English: UC-lc letter permutations at word start for glyphs {glyphs}\n"
    proof += gj_proof_en(glyphs, case="cap") + "\n\n"

    proof += f"English: UC-UC letter permutations inside word for glyphs {glyphs}\n"
    proof += gj_proof_en(glyphs, case="uc") + "\n\n"

    proof += f"English: lc-lc letter permutations inside word for glyphs {glyphs}\n"
    proof += gj_proof_en(glyphs, case="lc") + "\n\n"

    glyphs = "نيوفأعدقجزخضذئةىءآإ"
    proof += f"Arabic: letter permutations at word start for glyphs {glyphs}\n"
    proof += gj_proof_ar(glyphs, mode="init") + "\n\n"

    proof += f"Arabic: letter permutations inside word for glyphs {glyphs}\n"
    proof += gj_proof_ar(glyphs, mode="medi") + "\n\n"

    proof += f"Arabic: letter permutations at word end for glyphs {glyphs}\n"
    proof += gj_proof_ar(glyphs, mode="fina")

    print(proof)
