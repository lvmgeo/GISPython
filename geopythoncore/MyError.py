# -*- coding: utf-8 -*-
"""
     Error module
"""

class MyError(Exception):
    """Class for storing an error object"""
    def __init__(self, strerror):
        self.strerror = strerror
    def __str__(self):
        return self.strerror.encode('ascii', 'replace')
    def __unicode__(self):
        return self.strerror
