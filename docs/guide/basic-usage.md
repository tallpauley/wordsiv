# Basic Usage

## Importing WordSiv

Once you've [installed](../index.md#installation) WordSiv, try generating a
sentence:
```python
--8<-- "import.py"
```

You should see a random sentence in the console in the lower-right of DrawBot!

!!! Note
    If you want to experiment quickly with WordSiv functions, you can use
    `from wordsiv import *` syntax. Just be careful, it's not recommended as a
    good coding practice since collisions can happen and it becomes unclear
    on where the functions/variables are defined!

## Listing Vocabs

WordSiv generates text using [Vocabs](../../api-reference/#wordsiv.Vocab): objects that contain a word
list (usually with counts) for a given language. WordSiv includes some Vocabs, and you can
[make your own](adding-language-support.md). See all available vocabs with
`list_vocabs()`:

```python
--8<-- "list-vocabs.py"
```

## Selecting a Vocab

Set the Vocab to use for subsequent calls with `set_vocab()`:
```python
--8<-- "set-vocab.py"
```

You can also specify a Vocab as an argument:
```python
--8<-- "vocab-arg.py"
```

!!! Note
    The `vocab` arg has precedence over `set_vocab()`:
    ```python
    --8<-- "set-vocab-arg-precedence.py"
    ```

## Restricting the Glyph Set

Use `set_glyphs` to restrict which glyphs WordSiv can use:

```python
--8<-- "set-glyphs.py"
```

You can also specify `glyphs` as an argument:
```python
--8<-- "glyphs-arg.py"
```

!!! Note
    The `glyphs` arg has precedence over `set_vocab()`:
    ```python
    --8<-- "set-glyphs-arg-precedence.py"
    ```


You can also use it simply to select random words (or words ranked by occurence) that fit your criteria:

```python
from wordsiv import set_vocab, set_glyphs

# get random matching words
words(vocab="es", glyphs='hambugerfontsivñ', n_words=5, rnd=1, contains='ña')
# Returns: ['foránea', 'náufragos', 'estáis', 'fresán', 'trastámara']

# get most common matching words
top_words(vocab="ar", n_words=5, min_wl=3, glyphs='خشطغب')
# Returns: ['خطب', 'خطط', 'خشب', 'طبخ', 'بخط']
```