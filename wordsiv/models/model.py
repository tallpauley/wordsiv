from abc import ABC, abstractmethod


class Model(ABC):
    """The base class for all Models

    For convenience, it is based around single word generation. All that needs to be
    defined is filtered_model() and word() and all the other methods are based around
    these."""

    @classmethod
    @abstractmethod
    def filtered_model(cls, data, available_glyphs, font_info, rand, **kwargs):
        """Filter data from source, and return a new Model object"""
        pass

    def word(self, **kwargs):
        """Return a single word string"""
        raise NotImplementedError

    def words(self, num_words=None, cap_first=False, uc=False, lc=False, **kwargs):
        """Return a list of word strings"""

        if not num_words:
            num_words = self.rand.randrange(10, 20)

        # only capitalize first word if uc and lc not True
        should_cap_first = cap_first and not uc and not lc

        return [
            self.word(**kwargs, cap=(should_cap_first and n == 0))
            for n in range(num_words)
        ]

    def sentence(self, cap_sent=True, sent_len=10, term=True, **kwargs):
        """Return a sentence string"""

        # TODO: this is very English-centric, needs to be amended
        # By default a sentence is terminated with random punctuation
        terminators = [t for t in ".?!" if self.available_glyphs.have_glyphs(t)]
        if term and terminators:
            t = self.rand.choice(terminators)
        else:
            t = " "

        return (
            " ".join(self.words(num_words=sent_len, cap_first=cap_sent, **kwargs)) + t
        )

    def sentences(self, num_sents=5, **kwargs):
        """Return a list of sentence strings"""

        return [self.sentence(**kwargs) for _ in range(num_sents)]

    def paragraph(self, **kwargs):
        """Return a paragraph string"""

        return " ".join(self.sentences(**kwargs))

    def paragraphs(self, num_paras=3, **kwargs):
        """Return an iterable of paragraph strings"""

        return [self.paragraph(**kwargs) for _ in range(num_paras)]

    def text(self, **kwargs):
        """Return a string of a block of text"""

        return "\n\n".join(self.paragraphs(**kwargs))
