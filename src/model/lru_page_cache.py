import collections


class LRUPageCache:
    ''' LRU (least recently used) cache for storing transfermarkt parsed pages.'''

    def __init__(self, capacity):
        ''' Constructs new LRUPageCache isntance.

        Parameters
        ----------
            capacity : int
                Cache capacity.
        '''

        self._capacity = capacity
        self._cache = collections.OrderedDict()

    def get(self, key):
        ''' Returns value from cache by the key

        Parameters
        ----------
            key : int
                Key used to store the page (page number).

        Returns
        -------
            value stored by the key.
        '''

        try:
            value = self._cache.pop(key)
            self._cache[key] = value
            return value
        except KeyError:
            return -1

    def append(self, key, value):
        ''' Insert value by key into the cache.

        Parameters
        ----------
            key : int
                key used to store the page.

            value : PlayersPage
                the page itself.
        '''

        try:
            self._cache.pop(key)
        except KeyError:
            if len(self._cache) >= self._capacity:
                self._cache.popitem(last=False)
        self._cache[key] = value

    def is_cached(self, key):
        ''' Check if the key exists in the cache.

        Parameters
        ----------
            key : key to check

        Returns
        -------
            True if the key exists in the cache, False otherwise.
        '''

        return key in self._cache

    def get_all(self):
        ''' Returns all the cached pages.

        Returns
        -------
            OrderedDict instance.
        '''

        return self._cache

    def __getitem__(self, key):
        return self.get(key)
