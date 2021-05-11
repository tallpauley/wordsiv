#####################################################################################
###### DATA_WRAPPER
######################################################################################


class DataWrapper:
    """A generic data wrapper which stores it's hash on initialization

    This is so that big immutable data structures are only hashed once, allowing us to
    cache the filtering of data structures.
    """

    def __init__(self, data):
        self.data = data
        self.hash = hash(data)

    def __hash__(self):
        return self.hash

    def rehash(self):
        self.hash = hash(self.data)


def unwrap(datawrapper_class):
    """Decorator which feeds .data to the function, and returns result in DataWrapper"""

    def new_decorator(old_func):
        def new_func(*args, **kwargs):
            data = args[0].data
            result = old_func(data, *args[1:], **kwargs)
            return datawrapper_class(result)

        return new_func

    return new_decorator
