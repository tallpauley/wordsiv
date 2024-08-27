from wordsiv import set_model, word
from collections import defaultdict

ROUND_LEFT_LOWER = "cdeoq"
ROUND_RIGHT_LOWER = "bop"
FLAT_LEFT_LOWER = "bhiklmnpru"
FLAT_RIGHT_LOWER = "dhimnqu"
ROUND_LEFT_UPPER = "CGO"
ROUND_LEFT_UPPER = "DO"


def hoefler_style_proof(glyphs, suggest):

    set_model("en_prob_books")
    uc_glyphs = "".join(sorted(c for c in glyphs if c.isupper()))

    cap_words = []
    for cap_ltr in uc_glyphs:
        cap_words.extend(
            [
                word(
                    glyphs=glyphs,
                    case="cap",
                    regexp=rf"{cap_ltr}[{ROUND_LEFT_LOWER}].*",
                    idx=suggest[f"{cap_ltr}_round"],
                    min_wl=5,
                ),
                word(
                    glyphs=glyphs,
                    case="cap",
                    regexp=rf"{cap_ltr}[{FLAT_LEFT_LOWER}].*",
                    idx=suggest[f"{cap_ltr}_flat"],
                    min_wl=5,
                ),
            ]
        )

    p = " ".join(c for c in cap_words if c) + "."

    for cap_ltr in uc_glyphs:
        lc_ltr = cap_ltr.lower()
        words = [
            word(
                glyphs=glyphs,
                case="cap",
                regexp=rf"{cap_ltr}[{FLAT_LEFT_LOWER}].*",
                idx=suggest[f"{cap_ltr}_flat"],
                min_wl=5,
            ),
            word(
                glyphs=glyphs,
                case="lc",
                regexp=rf"{lc_ltr}[{FLAT_LEFT_LOWER}].*",
                idx=suggest[f"{lc_ltr}_flat"],
                min_wl=5,
            ),
            word(
                glyphs=glyphs,
                case="lc",
                regexp=rf"{lc_ltr}[{ROUND_LEFT_LOWER}].*",
                idx=suggest[f"{lc_ltr}_round"],
                min_wl=5,
            ),
            word(glyphs=glyphs, top_k=20),
            word(glyphs=glyphs, top_k=20),
            word(
                glyphs=glyphs,
                case="lc",
                regexp=rf".+[{FLAT_RIGHT_LOWER}]{lc_ltr}[{FLAT_LEFT_LOWER}].+",
                idx=suggest[f"flat_{lc_ltr}_flat"],
                min_wl=5,
            ),
            word(
                glyphs=glyphs,
                case="lc",
                regexp=rf".+[{ROUND_RIGHT_LOWER}]{lc_ltr}[{ROUND_LEFT_LOWER}].+",
                idx=suggest[f"round_{lc_ltr}_round"],
                min_wl=5,
            ),
            word(glyphs=glyphs, top_k=20),
            word(glyphs=glyphs, top_k=20),
            word(
                glyphs=glyphs,
                case="lc",
                regexp=rf".+[{FLAT_RIGHT_LOWER}]{lc_ltr}",
                idx=suggest[f"flat_{lc_ltr}"],
                min_wl=5,
            ),
            word(
                glyphs=glyphs,
                case="lc",
                regexp=rf".+[{ROUND_RIGHT_LOWER}]{lc_ltr}",
                idx=suggest[f"round_{lc_ltr}"],
                min_wl=5,
            ),
            word(glyphs=glyphs, top_k=20),
            word(glyphs=glyphs, top_k=20),
            word(
                glyphs=glyphs,
                case="lc",
                regexp=rf".+[{FLAT_RIGHT_LOWER}]{lc_ltr}{lc_ltr}[{FLAT_LEFT_LOWER}].+",
                idx=suggest[f"flat_{lc_ltr}{lc_ltr}_flat"],
                min_wl=5,
            ),
        ]
        sent = " ".join(w for w in words if w) + "."
        p += " " + sent

    return p


if __name__ == "__main__":
    glyphs = "HAMBUGERFONTSIVhambugerfontsiv.,"
    suggest = defaultdict(int)

    print(hoefler_style_proof(glyphs, suggest))


# by default we pull the most frequent word, n=0, but you can override the selection below for any combo
# suggest["H_flat"] = 1
