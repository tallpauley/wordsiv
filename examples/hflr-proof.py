"""WordSiv proof in the style of Jonathan Hoefler."""

from wordsiv import set_vocab, word, top_word

ROUND_L_LC = "cdeoq"
ROUND_R_LC = "bop"
FLAT_L_LC = "bhiklmnpru"
FLAT_R_LC = "dhimnqu"

FLAT_L_UC = "BDEFHIKLMNPR"
FLAT_R_UC = "HMN"
ROUND_L_UC = "CGOQ"
ROUND_R_UC = "DO"


def hflr_para_lc(glyphs):
    uc_glyphs = "".join(sorted(c for c in glyphs if c.isupper()))

    set_vocab("en")

    common_cap = {
        "min_wl": 5,
        "case": "cap",
        "glyphs": glyphs,
    }
    common_lc = {"min_wl": 5, "case": "lc", "glyphs": glyphs}

    cap_words = []
    for g in uc_glyphs:
        cap_words.extend(
            [
                top_word(idx=0, regexp=rf"{g}[{ROUND_L_LC}].*", **common_cap),
                top_word(idx=0, regexp=rf"{g}[{FLAT_L_LC}].*", **common_cap),
            ]
        )

    proof = " ".join(c for c in cap_words if c) + "."

    for g_uc in uc_glyphs:
        g_lc = g_uc.lower()
        words = [
            top_word(regexp=rf"{g_uc}[{FLAT_L_LC}].*", **common_cap),
            top_word(regexp=rf"{g_lc}[{FLAT_L_LC}].*", **common_lc),
            top_word(regexp=rf"{g_lc}[{ROUND_L_LC}].*", **common_lc),
            word(glyphs=glyphs, top_k=20),
            word(glyphs=glyphs, top_k=20),
            top_word(regexp=rf".+[{FLAT_R_LC}]{g_lc}[{FLAT_L_LC}].+", **common_lc),
            top_word(regexp=rf".+[{ROUND_R_LC}]{g_lc}[{ROUND_L_LC}].+", **common_lc),
            word(glyphs=glyphs, top_k=20),
            word(glyphs=glyphs, top_k=20),
            top_word(regexp=rf".+[{FLAT_R_LC}]{g_lc}", **common_lc),
            top_word(regexp=rf".+[{ROUND_R_LC}]{g_lc}", **common_lc),
            word(glyphs=glyphs, top_k=20),
            word(glyphs=glyphs, top_k=20),
            top_word(
                regexp=rf".+[{FLAT_R_LC}]{g_lc}{g_lc}[{FLAT_L_LC}].+", **common_lc
            ),
        ]
        sent = " ".join(w for w in words if w) + "."
        proof += " " + sent

    return proof


def hflr_para_uc(glyphs):
    uc_glyphs = "".join(sorted(c for c in glyphs if c.isupper()))
    set_vocab("en")

    common_uc = {"min_wl": 5, "case": "uc", "glyphs": glyphs}

    uc_sents = []
    for g in uc_glyphs:
        words = [
            top_word(regexp=rf"{g}[{FLAT_L_UC}].*", **common_uc),
            top_word(regexp=rf"{g}[{ROUND_L_UC}].*", **common_uc),
            word(glyphs=glyphs, case="uc", top_k=20),
            word(glyphs=glyphs, case="uc", top_k=20),
            top_word(regexp=rf".+[{FLAT_R_UC}]{g}[{FLAT_L_UC}].+", **common_uc),
            top_word(regexp=rf".+[{ROUND_R_UC}]{g}[{ROUND_L_UC}].+", **common_uc),
            word(glyphs=glyphs, case="uc", top_k=20),
            word(glyphs=glyphs, case="uc", top_k=20),
            top_word(regexp=rf".+[{FLAT_R_UC}]{g}", **common_uc),
            top_word(regexp=rf".+[{ROUND_R_UC}]{g}", **common_uc),
            word(glyphs=glyphs, case="uc", top_k=20),
            word(glyphs=glyphs, case="uc", top_k=20),
            top_word(regexp=rf".+[{FLAT_R_UC}]{g}{g}[{FLAT_L_UC}].+", **common_uc),
        ]
        uc_sents.append(" ".join(w for w in words if w) + ".")

    return " ".join(uc_sents)


if __name__ == "__main__":
    glyphs = "HAMBUGERFONTSIVhambugerfontsiv.,"

    print(hflr_para_lc(glyphs))
    print()
    print(hflr_para_uc(glyphs))
