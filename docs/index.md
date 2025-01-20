<p align="center">
  <a href="https://wordsiv.com"><img src="images/wordsiv-logo.png" alt="WordSiv"></a>
</p>
<p align="center">WordSiv is a Python library for generating proofing text for an incomplete
typeface.
</p>
<p align="center">
  <a href="https://github.com/tallpauley/wordsiv/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://github.com/tallpauley/wordsiv/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI">
  </a>
</p>

---

**Documentation**: [https://wordsiv.com](https://wordsiv.com)

**Source Code**: [https://github.com/tallpauley/wordsiv](https://github.com/tallpauley/wordsiv)

---

Say you've drawn `HAMBUGERFONTSIVhambugerfontsiv.,` and want a sentence with
*only* those glyphs:
```python
--8<-- "intro-example.py"
```

This returns something like:

>Bears run saint that fighting bargain remove, genre MA Barbara registration the
>bug it others entering Steven.

## Key Features

- **Shaped Text**: WordSiv generates text that is roughly the *shape* of text in
  the desired language using word/punctuation probabilities and capitalization.
- **Easy Word Filtering**: WordSiv selects from words that can be spelled with
  your current glyph set, so you don't have to worry about `.notdef`. Add
  additional word requirements (substrings, patterns, word length, etc.) on top
  without having to wrangle regex.
- **Letter Case Aware**: WordSiv has a simple `case` argument to set the desired
  case of words, and choose whether to transform letter case of the words in the
  Vocab. Words like `"I", "Paris", "DDoS", "WWF"` will by appear in their
  original letter case by default (if the Vocab has capitalization).

# Installation

### Installing in DrawBot

1. In the DrawBot menu, click **Python->Install Python Packages**:

2. Enter ```git+https://github.com/tallpauley/wordsiv``` and click **Go!**

![Screenshot of DrawBot "Install Python Packages"
Window](./images/drawbot-install.jpg)

#### Updating WordSiv in DrawBot

DrawBot caches Python packages/modules, so I'd recommend this process for
updating to the latest version of WordSiv:

1. In the DrawBot menu, click **Python->Install Python Packages**.
    - Click the dropdown **Install / Upgrade** and select **Uninstall**.
    - Enter `wordsiv` and click **Go!**.
4. Restart DrawBot.
5. Follow the [above instructions](#installing-in-drawbot) to install the latest
   version of WordSiv.


### Installing Outside of DrawBot

You can also install WordSiv on your system and use it in any Python script.
You'll probably want to use a [virtual environment][venv] or a
[Python tool][tool] that manages these for you, but I'll leave that up to you!

First make sure you have Python 3.9+. Then:

```bash
pip install git+https://github.com/tallpauley/wordsiv
```

## Why Simple Word Probability?

Proofing text doesn't necessarily have to be syntactically correct or have
meaning. It just needs the right amount of common and uncommon words to give it
a "realistic" *shape*. Often type designers do this manually, such as in
Jonathan Hoefler's fantastic [proof][proof]:
>Finally, I wanted the text to have the visual cadences of my native English, in
>which words of variable but digestible length are punctuated by shorter ones.

If we simply select words randomly, out of a hat which contains many more
duplicates of say, "the" than "etymology", we'll get a string of words which
visually resembles a sentence. This is how WordSiv works: sampling words from a
*probability distribution* which is determined by the occurrence counts of words
in a corpus of text.

Of course, the more we restrict our glyph set the more we've tampered with the
natural distribution of words, since most the longer, less-common words aren't
available (which make up the long tail of the [Zipf's law][zipf]).
However, we can blend in a bit of randomness to make it look like real text at a
glance!

This might be *more fun* [with LLMs](#other-resources), because the
glyph-limited text could potentially be both grammatically and semantically
correct. However, it remains to be seen if stability can be achieved while
filtering out the majority of tokens. And more importantly, why spend so much
more compute for so little payoff?

## Related Resources

### Software Tools Comparison

| Revocab | Type | Author | Glyphs Filtering | Algorithm | Probability |
| -- | -- | -- | -- | -- | -- |
| [WordSiv](#) | CLI | Chris Pauley | Yes | word probability (for now) | Yes |
| [Galvanized Jets][galvanized] | web tool | Samarskaya & Partners | No | static text | N/A |
| [Adhesion Text][adhesion] | web tool | Miguel Sousa | Yes | random word |  No |
| [Word-o-mat][wordomat] | Plugin | Nina Stössinger | No | random word | No
| [Test Text Generator][justanother] | web tool, [CLI][justanothercli] | Tim Ahrens | Yes | trigram character prediction | Yes |

### Other Resources

| Revocab | Author | Notes |
| -- | -- | -- |
| [Proof a Typeface][proof] | Jonathan Hoefler | A concise and comprehensive proof of illustrative English words, covering all round/flat spacing trigrams, including bigrams for sentence start/end and 4-grams for repeated letters. Made to look more text-like with joining phrases like "of the".
| [LLM Lipogram Guide][lipogram] | Corey Hanson | A really cool example of using LLMs for lipograms.
| [AI Writing Assistant][poets] | Allen Roush, Sanjay Basu, Akshay Moorthy, Dmitry Dubovoy | Another example of filtering the output of an LLM for lipogram generation and more.

[venv]: https://docs.python.org/3/library/venv.html
[tool]: https://www.reddit.com/r/Python/comments/16qz8mx/pipenv_piptools_pdm_or_poetry/
[proof]: https://jonathanhoefler.com/articles/how-to-proof-a-typeface
[zipf]: https://en.wikipedia.org/wiki/Zipf's_law#Word_frequencies_in_natural_languages
[galvanized]: https://www.galvanizedjets.com/
[adhesion]: https://adhesiontext.com/
[wordomat]: https://github.com/ninastoessinger/word-o-mat
[justanother]: https://justanotherfoundry.com/generator
[justanothercli]: https://github.com/justanotherfoundry/text-generator/tree/master
[lipogram]: https://coreyhanson.com/blog/a-simple-way-to-program-an-llm-lipogram/
[poets]: https://arxiv.org/abs/2306.15926
