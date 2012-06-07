from distutils.core import setup

setup(
	name = 'fastss',
	version = '0.095',
	author = 'Giorgos Tzampanakis',
	author_email = 'giorgos.tzampanakis@gmail.com',
	py_modules = ['fastss'],
	license = 'GPL',
	platforms = 'Any',
	description = 'String similarity searching using the FastSS algorithm.',
	long_description = """
		FastSS is a string similarity searching algorithm. For each query, which
		consists of query string *s* and distance *d*, it retrieves all the words in a
		dictionary whose edit distance from *s* is equal or smaller than *d*. FastSS is an
		offline searching algorithm, as it needs to create an index of its dictionary
		before it can search. For more information on FastSS you can visit the website
		of its inventors at <http://fastss.csg.uzh.ch/>.

		Here are some of the characteristics of this implementation, to help you decide
		whether it fits your purposes:

		* Very fast searching at the cost of a rather large index size.
		* Indices are plain sqlite databases so they carry ACID guarantees.
		* Only unicode strings are supported.

		Example of usage: ::

			>>> import fastss
			>>> manager = fastss.FastSSManager('idx')
			>>> manager.create_index(False)
			# Insert lemmas in the index, using 20% of their length as the depth:
			>>> manager.update_index([u'Mike', u'Johnny', u'johnny'], lambda s: int(len(s)*.2))
			# Search:
			>>> for match in manager.search('Mike', 2): print match
			(u'Mike', 0)
			>>> for match in manager.search('johnny', 1): print match
			(u'johnny', 0)
			(u'Johnny', 1)
			>>> for match in manager.search('johnny', 1, nocase=True): print match
			(u'Johnny', 0)
			(u'johnny', 0)
			>>> for match in manager.search('johny', 2, nocase=True): print match
			(u'johnny', 1)
			(u'Johnny', 1)
	""",
	classifiers = ['Programming Language :: Python',
					'License :: OSI Approved :: GNU General Public License (GPL)',
					'Operating System :: OS Independent',
					'Development Status :: 3 - Alpha',
					'Intended Audience :: Developers',
					'Topic :: Text Processing :: Indexing'
					]



)
