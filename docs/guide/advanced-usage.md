# Advanced Usage

## Object-Oriented API

You can also create and interact with `WordSiv` objects directly. In fact, the module-level functions actually do this under the hood, albeit with a single `WordSiv` object (singleton) that is instantiated when loading WordSiv:

```python
import wordsiv

# This sets vocab and glyphs defaults like set_vocab(), set_glyphs(), at object initialization
wsv_en = wordsiv.WordSiv(vocab='en', glyphs='hambugers')
wsv_fa = wordsiv.WordSiv(vocab='fa', glyphs='قنحثزعظلفع')

print(wsv_en.sent())
print(wsv_fa.sent())