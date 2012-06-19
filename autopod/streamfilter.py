#!/usr/bin/env python 
# coding: utf-8

''' Text wrapper for console output from http://wiki.python.org/moin/PrintFails '''

class StreamTee:
    
    """Intercept a stream.
    
    Invoke like so:
    sys.stdout = StreamTee(sys.stdout)
    
    See: grid 109 for notes on older version (StdoutTee).
    """
    
    def __init__(self, target):
        self.target = target
    
    def write(self, s):
        s = self.intercept(s)
        self.target.write(s)
    
    def intercept(self, s):
        """Pass-through -- Overload this."""
        return s


class SafeStreamFilter(StreamTee):
    """Convert string traffic to to something safe."""
    def __init__(self, target):
        StreamTee.__init__(self, target)
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding
    def intercept(self, s):
        return s.encode(self.encode_to, self.errors).decode(self.encode_to)


def console_mode():
    """Console mode."""
    import sys
    sys.stdout = SafeStreamFilter(sys.stdout)