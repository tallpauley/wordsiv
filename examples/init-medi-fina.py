"""WordSiv proof that is an adaption of a proof from @jmsole"""

from wordsiv import top_words, set_vocab

# Arabic and Farsi glyphs
ar_glyphs = "ابجدهوزحطيكلمنسعفصقرشتثخذضظغء"
fa_glyphs = "یهونملگکقفغعظطضصشسژزرذدخحچجثتپباء"


def init_medi_fina(glyphs, lang):

    set_vocab(lang)
    lines = []
    for g in glyphs:
        init = " ".join(top_words(n_words=5, min_wl=5, max_wl=14, startswith=g))
        medi = " ".join(top_words(n_words=5, min_wl=5, max_wl=14, inner=g))
        fina = " ".join(top_words(n_words=5, min_wl=5, max_wl=14, endswith=g))
        lines.append(g + " " + " ".join([init, medi, fina]))

    return "\n".join(lines)


if __name__ == "__main__":
    # Generate and print text proofs for Arabic and Farsi templates
    print("Proof text in Farsi:")
    print(init_medi_fina(fa_glyphs, lang="fa"))

    print("Proof text in Arabic:")
    print(init_medi_fina(ar_glyphs, lang="ar"))
