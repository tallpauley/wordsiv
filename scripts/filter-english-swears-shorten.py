import json


# https://github.com/reimertz/curse-words
with open("reimertz_curse-words.json", "r") as f:
    swears1 = json.load(f)["words"]

# https://github.com/MauriceButler/badwords
with open("maurice-butler_badwords.json", "r") as f:
    swears2 = json.load(f)["words"]

# en version of
# https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words/
swears3 = []
with open("LDNOOBW.txt", "r") as f:
    for l in f:
        swears3.append(l.strip())

swears_exact = set(swears1 + swears2 + swears3)
swears_exact.remove("Nobody")
swears_exact.remove("escort")
swears_exact.remove("poop")
swears_exact.add("titjob")
swears_exact.add("titjobs")
swears_exact.add("pakis")
swears_exact.add("paki")
swears_exact.add("coon")
swears_exact.add("coons")
swears_exact.add("mong")
swears_exact.add("mongs")
swears_exact.add("mongs")

# whitelist wordi
whitelisted = set(
    (
        "nazim",
        "coauthored",
        "eurostoxx",
        "essex",
        "sequimalt",
        "kumari",
        "cockles",
        "sclerotic",
        "pachinko",
        "metrosexual",
        "pricked",
        "xxs",
        "cocooons",
        "middlesex",
        "transexuals",
        "vioxx",
        "therapists",
        "scattering",
        "coke",
        "cocktail",
        "xxl",
        "knobs",
        "unisex",
        "hancock",
        "montenegro",
        "therapist",
        "transsexual",
        "milford",
        "knobs",
        "cummings",
        "debugger",
        "hitchcock",
        "lolitas",
        "wilcox",
        "escorted",
        "spawning",
        "cockpit",
        "breaststroke" "sexton",
        "duchess",
        "woodpecker",
        "xxi",
        "maxx",
        "pharmacokinetics",
        "hwang",
        "twinkle",
        "shaggy",
        "footballs",
        "babcock",
        "fukuoka",
        "dickerson",
        "scraping",
        "cockburn",
        "cxx",
        "flanges",
        "atwater",
        "riddick",
        "prickly",
        "cockroach" "thumping",
        "dickinson",
        "peacock",
        "debugger",
        "middlesex",
        "coke",
        "kumar",
        "dickinson",
        "unisex",
        "milford",
        "sussex",
        "middlesex",
        "coke",
        "wessex",
        "retardant",
        "spoofing",
        "matsushita",
        "wanganui",
        "nazionale",
        "snatched",
        "roddick",
        "sadistic",
        "pawnee",
        "scunthorpe",
        "dickie",
        "etobicoke",
        "dinky",
        "seguro",
        "moorcock",
        "vecchio",
        "cocky",
        "xxxl",
        "thorny",
        "thumping",
        "thumbsucker",
        "willys",
        "psychotherapist",
        "pawns",
        "pawns",
        "fago",
        "bismuth",
        "twinkling",
        "forkum",
        "internazionale",
        "pysiotherapists",
        "yamashita",
        "fukushima",
        "suckling",
        "twang",
        "ashkenazi",
        "raccoons",
        "spoofs",
        "negroponte",
        "fukuda",
        "cockney",
        "petits",
        "skeeter",
        "duchesne",
        "atherosclerotic",
        "willcox",
        "tittel",
        "Dicken",
        "akumal",
        "okuma",
        "retardants",
        "hypnotherapist",
        "transmutation",
        "asexual",
        "alcock",
        "dicky",
        "cockatiel",
        "yoakum",
        "pa",
        "sextile",
        "wnbrokers",
        "kumi",
        "tittle",
        "kumamoto",
        "civitave",
        "fukuyama",
        "cchia",
        "joaquim",
        "cocking",
        "coxon",
        "dokumentation",
        "doorknob",
        "wilcoxon",
        "pocock",
        "vandyke",
        "ishiguro",
        "fagen",
        "thermoforming",
        "kuma",
        "quimper",
        "pooped",
        "takumi",
        "draping",
        "retarding",
        "nymphomanin",
        "cocoons",
        "dokumente",
        "rajkumar",
        "fagin",
        "sparxxx",
        "pooping",
        "pawnbrokers",
        "azimuthal",
        "fukui",
        "xxxviii",
        "kwang",
        "physiotherapist",
        "dickenson",
        "paclitaxel",
        "woodcock",
        "swank",
        "phuket",
        "dickens",
        "spawned",
        "sexton",
        "honeysuckle",
        "quimby",
        "burdick",
        "cockroaches",
        "xxxi",
        "xxxii",
        "celecoxib",
        "sequim",
        "chessex",
        "xxxiii",
        "xxxv",
        "dokument",
        "spasticity",
        "xxxvi",
        "stitt",
        "reddick",
        "kumho",
        "porgy",
        "nanticoke",
        "civitavecchia",
        "laycock",
        "bucetation",
        "secchi",
        "rofecoxib",
        "coxx",
        "kinoshita",
    )
)

all_whitelisted = set()

# make plurals and singulars
for w in whitelisted:
    if w.endswith("s"):
        all_whitelisted.add(w[0:-1])
    else:
        all_whitelisted.add(w + "s")

    all_whitelisted.add(w)

# these words are searched for inside the word string
# these are being taken off the list, since they are often part of regular words
swears_partial = set(swears1 + swears2 + swears3)
swears_partial.add("muffdiv")
for word in (
    "tit",
    "bum",
    "ass",
    "asses",
    "butt",
    "crap",
    "homo",
    "anal",
    "anus",
    "jap",
    "cum",
    "semen",
    "hell",
    "turd",
    "lust",
    "cipa",
    "spac",
    "poon",
    "rape",
    "spic",
    "damn",
    "paki",
    "coon",
    "cialis",
    "cums",
    "mong",
    "Nobody",
    "nob",
    "arse",
    "pron",
    "hore",
    "scat",
    "balls",
    "rimming",
    "twat",
    "xx",
    "hoar",
    "spunk",
    "escort",
    "muff",
    "poop",
):
    swears_partial.remove(word)

wc = 0
word_counts = []
# wordslist is https://norvig.com/ngrams/count_1w.txt
with open("count_1w.txt", "r") as source_file, open(
    "eng-most-common.txt", "w+"
) as dest_file:
    for l in source_file:
        word, count = l.strip().split()

        # pass if exact match for swear
        if word in swears_exact:
            continue

        # only keep word if partial swear not in word
        if word in all_whitelisted or all(s not in word for s in swears_partial):
            dest_file.write("\t".join((word, count)) + "\n")
            wc += 1
