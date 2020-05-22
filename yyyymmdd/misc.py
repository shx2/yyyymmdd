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
