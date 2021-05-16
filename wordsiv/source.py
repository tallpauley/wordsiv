class BaseSource:
    @property
    def data(self):
        """Return data to be filtered and loaded into a model

        The data should be loaded only when this method is called. This allows Wordsiv
        to instantiate many Sources quickly, and only do costly loads when called for.

        For this reason, you should use decorator @lru_cache(maxsize=None) so the data
        only needs to be loaded the first time data is requested
        """
        raise NotImplementedError

    def meta(self):
        """return metadata dictionary"""

        return self.meta
