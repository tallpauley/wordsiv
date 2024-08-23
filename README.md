
# WordSiv

WordSiv is a Python library/framework for generating text  with on a limited glyph set for [proofing typefaces](https://ohnotype.co/blog/proof-it). Here is an example using simple word probability from a huge corpus of books:
```python
>>> from wordsiv import set_model, sent
>>> set_model('en_prob_books')
>>> sent(glyphs='HAMBUGERFONTSIVhambugerfontsiv.,')
'A reform about for beer environment to the ease movie this if not no the on.'
```

## Why?

When designing a typeface, it's important to evaluate the typeface in text while the glyph set is limited. Tools like [word-o-mat](https://github.com/ninastoessinger/word-o-mat) are great for evaluating words, but lack the ability to make "realistic-looking" text which is punctuated by common words.

Also, I felt the need for an easy-to-use, extensible library for word/text generation to drop into [DrawBot](https://www.drawbot.com/) for dynamic type proof creation.


## Installation in DrawBot

1. Install the `wordsiv` package via **Python->Install Python Packages**:
     - Enter ```git+https://github.com/tallpauley/wordsiv``` and click **Go!**
     - ***Note:*** you'll probably see lots of red text but it
       should still work just fine

    ![Screenshot of DrawBot "Install Python
    Packages" Window](docs/images/drawbot-install.jpg)

2. Install the desired Source packages in the same window:

    ```git+http://github.com/tallpauley/wordsiv-sources```

3. You can now 


## Installation

First, install wordsiv with pip:

```bash
$ pip install git+https://github.com/tallpauley/wordsiv # byexample: +pass
```

Then install some **sources**:

```bash
pip install git+https://github.com/tallpauley/wordsiv-sources
```

## Examples


## Related Resources

### Software Tools Comparison
| Resource | Type | Author | Glyphs Filtering | Algorithm | Probability |
| -- | -- | -- | -- | -- | -- |
| [WordSiv](#) | CLI | Chris Pauley | Yes | word probability (for now) | Yes |
| [Galvanized Jets](https://www.galvanizedjets.com/) | web tool | Samarskaya & Partners | No | static text | N/A |
| [adhesiontext.com](https://adhesiontext.com/) | web tool | Miguel Sousa | Yes | random word |  No |
| [word-o-mat](https://github.com/ninastoessinger/word-o-mat) | Robofont & Glyphs plug-in | Nina Stössinger | random word | random word | No
| [Just Another Test Text Generator](https://justanotherfoundry.com/generator) | web tool, [CLI](https://github.com/justanotherfoundry/text-generator/tree/master) | Tim Ahrens | Yes | trigram character prediction | Yes |

### Other Resources
| Resource | Author | Notes |
| -- | -- | -- |
| [How to Proof a Typeface](https://jonathanhoefler.com/articles/how-to-proof-a-typeface) | Jonathan Hoefler | A concise and comprehensive proof of illustrative English words, covering all round/flat spacing trigrams, including bigrams for sentence start/end and 4-grams for repeated letters. Made to look more text-like with joining phrases like "of the".
| [A Simple Way to Program an LLM Lipogram](https://coreyhanson.com/blog/a-simple-way-to-program-an-llm-lipogram/) | Corey Hanson | A really cool example of using LLMs for lipograms.
| [Most Language Models can be Poets too: An AI Writing Assistant and Constrained Text Generation Studio](https://arxiv.org/abs/2306.15926) | Allen Roush, Sanjay Basu, Akshay Moorthy, Dmitry Dubovoy | Another example of filtering the output of an LLM for lipogram generation and more.