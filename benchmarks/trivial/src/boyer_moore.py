# Copyright (c) 2012 the authors listed at the following URL, and/or
# the authors of referenced articles or incorporated external code:
# http://en.literateprograms.org/Boyer-Moore_string_search_algorithm_(Python)?action=history&offset=20120323184109
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# Retrieved from: http://en.literateprograms.org/Boyer-Moore_string_search_algorithm_(Python)?oldid=18108


def match(pattern, text):
	matches = []
	m = len(text)
	n = len(pattern)

	rightMostIndexes = preprocessForBadCharacterShift(pattern)	
	alignedAt = 0
	while alignedAt + (n - 1) < m:
		for indexInPattern in xrange(n-1, -1, -1):
			indexInText = alignedAt + indexInPattern
			x = text[indexInText]
			y = pattern[indexInPattern]
			if indexInText >= m:
				break
			if x != y:
				r = rightMostIndexes.get(x)
				if x not in rightMostIndexes:
					alignedAt = indexInText + 1
				else:
					shift = indexInText - (alignedAt + r)
					alignedAt += (shift > 0 and shift or 1)
				break
			elif indexInPattern == 0:
				matches.append(alignedAt)
				alignedAt += 1

	return matches

def preprocessForBadCharacterShift(pattern):
	map = { }
	for i in xrange(len(pattern)-1, -1, -1):
		c = pattern[i]
		if c not in map:
			map[c] = i
	return map

if __name__ == "__main__":
	matches = match("ana", "bananas")
	for integer in matches:
		print "Match at:", integer
	print (matches == [1, 3] and "OK" or "Failed")
