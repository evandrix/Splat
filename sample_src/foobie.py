#!/usr/bin/env python

class foobie:
    def bletch(self):
        print "foobie bletch"

def blatch(self):
    print "I am the monkey that will rule the world"
foobie.bletch = blatch

if __name__ == "__main__":
    maud = foobie()
    maud.bletch()
