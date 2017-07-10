# -*- coding: utf-8 -*-
"""
     Error module
"""

class MyError(Exception):
    """Class for storing an error object"""
    def __init__(self, strerror):
        self.strerror = strerror
    def __str__(self):
        try: # string
            return str(self.strerror)
        except Exception:
            pass
            
        try: # unicode
            value = unicode(self.strerror)
            return value.encode("ascii", "backslashreplace")
        except Exception:
            pass
            
        try: # repr
            value = self.strerror.repr()
            return value
        except Exception:
            pass
            
        return '<unprintable %s object>' % type(value).__name__
    def __repr__(self):
        return self.__str__()
    def __unicode__(self):
        return self.strerror
