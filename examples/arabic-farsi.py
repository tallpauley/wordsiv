from wordsiv import sent
import time

# Arabic and Farsi character templates
ar_glyphs = "ابجدهوزحطيكلمنسعفصقرشتثخذضظغء"
fa_glyphs = "یهونملگکقفغعظطضصشسژزرذدخحچجثتپباء"


def init_medi_fina(glyphs, lang):
    textProofString = ""

    lines = []
    for g in glyphs:
        line = g + ". "
        line += " ".join(
            [
                sent(
                    model=lang, seq=True, num_words=5, min_wl=5, max_wl=14, startswith=g
                ),
                sent(model=lang, seq=True, num_words=5, min_wl=5, max_wl=14, inner=g),
                sent(
                    model=lang, seq=True, num_words=5, min_wl=5, max_wl=14, endswith=g
                ),
            ]
        )
        lines.append(line)

    return "\n".join(lines)


if __name__ == "__main__":
    # Generate and print text proofs for Arabic and Farsi templates
    print("Proof text in Farsi:")
    print(init_medi_fina(fa_glyphs, lang="fa"))

    print("Proof text in Arabic:")
    print(init_medi_fina(ar_glyphs, lang="ar"))
