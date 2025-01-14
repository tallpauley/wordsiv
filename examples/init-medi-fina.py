"""WordSiv proof that is an adaption of a proof from @jmsole"""

from wordsiv import WordSiv

# Arabic and Farsi glyphs
AR_GLYPHS = "ابجدهوزحطيكلمنسعفصقرشتثخذضظغء"
FA_GLYPHS = "یهونملگکقفغعظطضصشسژزرذدخحچجثتپباء"


def init_medi_fina(glyphs, lang):
    wsv = WordSiv(glyphs=glyphs, vocab=lang)

    lines = []
    for g in glyphs:
        init = " ".join(wsv.top_words(n_words=5, min_wl=5, max_wl=14, startswith=g))
        medi = " ".join(wsv.top_words(n_words=5, min_wl=5, max_wl=14, inner=g))
        fina = " ".join(wsv.top_words(n_words=5, min_wl=5, max_wl=14, endswith=g))
        lines.append(g + " " + " ".join([init, medi, fina]))

    return "\n".join(lines)


if __name__ == "__main__":
    # Generate and print text proofs for Arabic and Farsi templates
    print("Proof text in Farsi:")
    print(init_medi_fina(FA_GLYPHS, lang="fa"))

    print("Proof text in Arabic:")
    print(init_medi_fina(AR_GLYPHS, lang="ar"))
