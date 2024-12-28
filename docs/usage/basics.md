# Basic Usage

If you're used to using DrawBot, the module-level functions should be easiest for you to use:

```python
from wordsiv import sent, para

print(sent(vocab='en'))
print(para(vocab='en'))
```

OR, you can keep the functions namespaced. Say, for avoiding a collison with DrawBot's `text()`:

```python
import wordsiv

print(wordsiv.text(vocab='en'))
```

You can also avoid collisions with the use of `as` in import statements:

```python
from wordsiv import text as txt

print(txt(vocab='en'))
```

## Setting Default Glyphs and Vocab

You might not want to specify `vocab` and `glyphs` every time you call `para()`. You can use `set_vocab()` and `set_glyphs()` to avoid having to type these as parameters:

```python
from wordsiv import set_vocab, set_glyphs, para

set_vocab('en')
set_glyphs('HAMBUGERFONTShambugerfonts')

print(para())
```

## Object-Oriented API

You can also create and interact with `WordSiv` objects. In fact, the module-level functions actually do this under the hood, albeit with a single `WordSiv` object (singleton) that is instantiated when loading WordSiv:

```python
import wordsiv

wsv_en = wordsiv.WordSiv(glyphs='hambugers')
wsv_fa = wordsiv.WordSiv(vocab='fa', glyphs='قنحثزعظلفع')

print(wsv_en.sent())
print(wsv_fa.sent())

```
