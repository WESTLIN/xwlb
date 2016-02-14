#!/usr/bin/env python
#coding=utf-8

import hashlib
from time import time
from itertools import izip
from functools import wraps
try:
    import cPickle as pickle
except ImportError:
    import pickle


class BaseCache(object):
    def __init__(self, timeout=300):
        self.timeout = timeout
    
    def get(self, key):
        return None
    
    def get_many(self, *keys):
        return map(self.get, keys)
    
    def get_dict(self, *keys):
        return dict(izip(keys, self.get_many(*keys)))
    
    def set(self, key, value, timeout=None):
        pass
    
    def delete(self, key):
        pass

    def clear(self):
        pass

    def mark_key(self, function, args, kwargs):
        try:
            key = pickle.dumps((function.func_name, args, kwargs))
        except:
            key = pickle.dumps(function.func_name)
        return hashlib.sha1(key).hexdigest()

    def cached(self, timeout=None, unless=None):
        """
        Example:
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)
    
                key = self.mark_key(f, args, kwargs)
    
                rv = self.get(key)
    
                if rv is None:
                    rv = f(*args, **kwargs)
                    self.set(key, rv, timeout=timeout)
    
                return rv
            return decorated_function
        return decorator


class SimpleCache(BaseCache):
    def __init__(self, threshold=100000, timeout=86400*30):
        BaseCache.__init__(self, timeout)
        self._cache = {}
        self._threshold = threshold
    
    def _prune(self):
        if len(self._cache) >= self._threshold:
            num = len(self._cache) - self._threshold + 1
            for key, value in sorted(self._cache.items(), key=lambda x:x[1][0])[:num]:
                self._cache.pop(key, None)
    
    def get(self, key):
        expires, value = self._cache.get(key, (0, None))
        if expires > time():
            return pickle.loads(value)
        
    def set(self, key, value, timeout=None):
        if timeout is None:
            timeout = self.timeout
        self._prune()
        self._cache[key] = (time() + timeout, pickle.dumps(value, 
            pickle.HIGHEST_PROTOCOL))
    
    def delete(self, key):
        self._cache.pop(key, None)

    def clear(self):
        for key, (expires, _) in self._cache.iteritems():
            if expires < time():
                self._cache.pop(key, None)


cache = SimpleCache()


def cached(func):

    def handle_func(self, *args):
        keys = [self.__class__.__name__, func.__name__]
        for i in args:
            keys.append('_%s' % i)
        key = ''.join(keys)
        rv = cache.get(key)
        if rv is not None:
            return rv
        rv = func(self, *args)
        cache.set(key, rv)
        return rv
    return handle_func
