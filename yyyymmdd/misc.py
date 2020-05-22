"""
Misc tools used in this pacakge.
"""

import functools


class classproperty(object):

    def __init__(self, fget):
        self.fget = classmethod(fget)
        functools.update_wrapper(self, fget)

    def __get__(self, *a):
        return self.fget.__get__(*a)()


def egcd(a, b):
    """ Return a triple (g, x, y), where ax + by = g = gcd(a, b) """
    x, y, u, v = 0, 1, 1, 0
    while a:
        q, r = b // a, b % a
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
    return b, x, y
