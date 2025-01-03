from wordsiv import set_vocab, set_glyphs, sent, word

set_vocab("en")
set_glyphs("HAMBUGERFONThambugerfont")

# same results
sent(seed=3)
"Heart tent terra Emma root buffet foam mom Hagen to earth at ammo"
sent(seed=3)
"Heart tent terra Emma root buffet foam mom Hagen to earth at ammo"

# not if we change our glyphs though!
set_glyphs("HAMBUGERFONTSIVhambugerfontsiv")
sent(seed=3)
"Of not but not to as on to setting the of the things"

# you only need to seed at the beginning of your proof
(word(seed=1), word())
("of", "agreement")
(word(seed=1), word())
("of", "agreement")

# so as long as you don't insert a new call
(word(seed=1), word(startswith="f"), word())
("of", "fee", "area")
