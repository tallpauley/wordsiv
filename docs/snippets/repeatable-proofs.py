from wordsiv import WordSiv

wsv = WordSiv(vocab="en", glyphs="HAMBUGERFONThambugerfont")

# same results
print(wsv.sent(seed=3))
# "Heart tent terra Emma root buffet foam mom Hagen to earth at ammo"
print(wsv.sent(seed=3))
# "Heart tent terra Emma root buffet foam mom Hagen to earth at ammo"

# not if we change our glyphs though!
wsv.default_glyphs = "HAMBUGERFONTSIVhambugerfontsiv"
print(wsv.sent(seed=3))
# "Of not but not to as on to setting the of the things"

# you only need to seed at the beginning of your proof:
wsv.seed(1)
print(wsv.word())
# "of"
print(wsv.word())
# "agreement"

# See? same results as above:
wsv.seed(1)
print(wsv.word())
# "of"
print(wsv.word())
# "agreement"

# so as long as you don't insert a new call which uses the random generator in-between:
wsv.seed(1)
print(wsv.word())
# "of"
print(wsv.word(startswith="f"))
# "fee"
print(wsv.word())
# "area"
