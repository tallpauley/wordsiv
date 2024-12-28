# Importing and Using WordSiv

There are a couple different ways to import and work with WordSiv. If you've only ever worked with Python in DrawBot, the module-level functions should be easiest for you to use:

```python
from wordsiv import sent, para

print(sent(vocab='en'))
print(para(vocab='en'))
```

Nice and short syntax! Just **be careful when importing functions this way.** For example, you could accidentally replace DrawBot's `text()` function with `wordsiv.text()`. One solution is to import `wordsiv.text()` as `txt()`:

```python
from wordsiv import text as txt

print(txt(vocab='en'))
```

Another way to avoid collisions is just using the `wordsiv` module namespace (at least just for `text()`). In the words of the [Zen of Python](https://en.wikipedia.org/wiki/Zen_of_Python): "Namespaces are one honking great idea":

```python
import wordsiv

# wordsiv.text() makes multiple paragraphs separated by double line breaks
print(wordsiv.text(vocab='en'))
```

## Setting Default Glyphs and Vocab

You might not want to specify `vocab` and `glyphs` every time you call a WordSiv function such as `para()`. You can use `set_vocab()` and `set_glyphs()` to avoid having to type these as parameters:

```python
from wordsiv import set_vocab, set_glyphs, para

set_vocab('en')
set_glyphs('HAMBUGERFONTShambugerfonts')

print(para())
```

## Object-Oriented API

You can also create and interact with `WordSiv` objects directly. In fact, the module-level functions actually do this under the hood, albeit with a single `WordSiv` object (singleton) that is instantiated when loading WordSiv:

```python
import wordsiv

# This sets vocab and glyphs defaults like set_vocab(), set_glyphs(), at object initialization
wsv_en = wordsiv.WordSiv(vocab='en', glyphs='hambugers')
wsv_fa = wordsiv.WordSiv(vocab='fa', glyphs='قنحثزعظلفع')

print(wsv_en.sent())
print(wsv_fa.sent())

```
