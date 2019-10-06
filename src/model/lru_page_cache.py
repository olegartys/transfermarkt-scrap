import collections


class LRUPageCache:
    def __init__(self, capacity):
        self._capacity = capacity
        self._cache = collections.OrderedDict()

    def get(self, key):
        try:
            value = self._cache.pop(key)
            self._cache[key] = value
            return value
        except KeyError:
            return -1

    def append(self, key, value):
        try:
            self._cache.pop(key)
        except KeyError:
            if len(self._cache) >= self._capacity:
                self._cache.popitem(last=False)
        self._cache[key] = value

    def is_cached(self, key):
        return key in self._cache

    def get_all(self):
        return self._cache

    def __getitem__(self, key):
        return self.get(key)
