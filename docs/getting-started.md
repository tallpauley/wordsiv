# Getting Started

## Installation in DrawBot

Install the `wordsiv` package via **Python->Install Python Packages**:

- Enter ```git+https://github.com/tallpauley/wordsiv``` and click **Go!**
- ***Note:*** you'll probably see lots of red text but it
should still work just fine

    ![Screenshot of DrawBot "Install Python
    Packages" Window](images/drawbot-install.jpg)

## Basic Usage

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