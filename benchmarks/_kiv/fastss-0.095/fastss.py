#!/usr/bin/python

import sys, sqlite3, uuid, os
import itertools
import cPickle, copy

# fastss -- String similarity searching using the FastSS algorithm.
# Copyright (C) 2011 Giorgos Tzampanakis
#
# fastss is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# fastss is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# fastss.  If not, see <http://www.gnu.org/licenses/>.

sqlite3.enable_callback_tracebacks(True)

class FastSSManager:
	""" A FastSSManager is associated with a fastss index (not to be confused
	with an sqlite database index, which is also used, discussed later.)

	Example of usage:

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
	
	 """

	_idx = 'fragments_index'
	_nocase_idx = 'fragments_nocase_index'
	_delete_idx = 'fragments_delete_index'

	def __init__(self, filename):
		""" filename refers to the index to be used. If the file doesn't exist
		it will not be created on the filesystem, only its filename will be
		remembered so that the index proper can be created using the
		create_index function. """

		self.filename = filename
		self.index_created = os.path.exists(self.filename)

	def create_index(self, include_user_field=False, accelerate_nocase=True, accelerate_deletes=True, accelerate_case=True):
		""" Create the internal structure of the index. For information on the
		include_user_field parameter, see the update_index function. The final
		three parameters specify whether or not to accelerate (use sql indices)
		searches and deletions. Each "acceleration" will slightly reduce the
		index updating performance. Note that accelerate_case and
		accelerate_nocase should not be both disabled at the same time, as
		searches will be tremendously slow. """

		if self.index_created: raise FastSSException('Index has already been created.', 'index_created')
		c = sqlite3.connect(self.filename)
		c.execute('begin transaction')
		c.execute('''create table lemmas(
				lemma_id integer primary key autoincrement,
				lemma text not null
				%s)''' % (', user_field text' if include_user_field else ''))
		c.execute('''create table fragments(
				fragment_id primary key,
				fragment text not null, 
				deletion_sequence blob not null,
				total_deletions integer not null check (total_deletions>=0),
				lemma_id integer references lemmas)''')
		if accelerate_case:
			c.execute('''create index %s on fragments(fragment, total_deletions asc)''' % self._idx)
		if accelerate_nocase:
			c.execute('''create index %s on fragments(fragment collate nocase, total_deletions asc)''' % self._nocase_idx)
		if accelerate_deletes:
			c.execute('''create index %s on fragments(lemma_id)''' % self._delete_idx)
		c.commit()
		self.index_created = True
		self.include_user_field = True
		c.close()

	def accelerate_case(self):
		""" Accelerate case-sensitive searches. """
		c = sqlite3.connect(self.filename)
		try:
			c.execute('''create index %s on fragments(fragment, total_deletions asc)''' % self._idx)
		except sqlite3.OperationalError, oe:
			if oe.args[0]=='index %s already exists' % self._idx:
				raise FastSSException('Case-sensitive searches are already accelerated.', 'case_index_exists')
			else:
				raise
		c.close()

	def accelerate_nocase(self):
		""" Accelerate case-insensitive searches. """
		c = sqlite3.connect(self.filename)
		try:
			c.execute('''create index %s on fragments(fragment, total_deletions asc)''' % self._nocase_idx)
		except sqlite3.OperationalError, oe:
			if oe.args[0]=='index %s already exists' % self._nocase_idx:
				raise FastSSException('Case-insensitive searches are already accelerated.', 'nocase_index_exists')
			else:
				raise
		c.close()

	def decelerate_case(self):
		""" Decelerate case-sensitive searches. """
		c = sqlite3.connect(self.filename)
		try:
			c.execute('''drop index %s''' % self._idx)
		except sqlite3.OperationalError, oe:
			if oe.args[0]=='no such index: %s' % self._idx:
				raise FastSSException('Case-sensitive searches are not accelerated.', 'case_index_does_not_exist')
			else:
				raise

		c.close()
		
	def decelerate_nocase(self):
		""" Decelerate case-insensitive searches. """
		c = sqlite3.connect(self.filename)
		try:
			c.execute('''drop index %s''' % self._nocase_idx)
		except sqlite3.OperationalError, oe:
			if oe.args[0]=='no such index: %s' % self._nocase_idx:
				raise FastSSException('Case-insensitive searches are not accelerated.', 'case_index_does_not_exist')
			else:
				raise

		c.close()

	def accelerate_deletes(self):
		""" Accelerate deletes from the index. """
		c = sqlite3.connect(self.filename)
		try:
			c.execute('''create index %s on fragments(fragment, total_deletions asc)''' % self._delete_idx)
		except sqlite3.OperationalError, oe:
			if oe.args[0]=='index %s already exists' % self._delete_idx:
				raise FastSSException('Deletes are already accelerated.', 'deletes_index_exists')
			else:
				raise
		c.close()

	def decelerate_deletes(self):
		""" Decelerate deletes from the index. """
		c = sqlite3.connect(self.filename)
		try:
			c.execute('''drop index %s''' % self._delete_idx)
		except sqlite3.OperationalError, oe:
			if oe.args[0]=='no such index: %s' % self._delete_idx:
				raise FastSSException('Deletes are not accelerated.', 'deletes_index_does_not_exist')
			else:
				raise

		c.close()
		
	def delete_from_index(self, lemmas):
		""" Delete the contents of the lemmas sequence from the index. """
		c=sqlite3.connect(self.filename)
		c.executemany('''delete from fragments where lemma_id = 
							(select lemma_id from lemmas where lemma=?)''',
							(lemmas,))
		c.executemany('''delete from lemmas where lemma=?''', (lemmas,))
		c.commit()
		c.close()
							

	def update_index(self, lemmas, depth_callback, user_fields = None):
		""" Update the index with the contents of the lemmas sequence, which
		should be unicode strings. Please don't use non-unicode strings unless
		you like subtle bugs. 
		
		depth_callback is a function that accepts a
		string as a parameter and returns an integer. The function will be
		applied to each lemma to determine the depth to which it will be
		indexed. 
		
		If the index has been created with user_fields (see the
		documentation for the __init__ function) then user_fields can
		optionally be a sequence of the same length with lemmas, each
		user_field will be associated with its respective lemma and it will be
		returned with said lemma when it is a search result. """

		if user_fields!=None:
			user_fields = user_fields.__iter__()

		if user_fields and not self.include_user_field:
			raise FastSSException('This index has not been created with user fields.', 'no_user_fields')
		c=sqlite3.connect(self.filename)
		c.execute('begin transaction')

		inserts = 0
		try:
			for lemma in lemmas:

				c.execute('''insert into lemmas (lemma %s) values
						(?%s)''' % (',user_field' if user_fields else '', ',?' if user_fields else ''), (lemma,user_fields.next()) if user_fields else (lemma,))

				lemma_id = c.execute("select seq from sqlite_sequence where name='lemmas'").fetchone()[0]
				g = (triple+[lemma_id] for triple in _wrap_fastss_generator(_delneigh(lemma, depth_callback(lemma))))
				c.executemany('''insert into fragments (fragment, deletion_sequence, total_deletions, lemma_id) values (?,?,?,?)''',g)

			c.commit()
		finally:
			c.close()
			pass
			

	def analyze(self):
		""" Reanalyze the index to enable faster searching. It is only useful
		to call this function When significant amount (in the order of tens of
		thousands) of lemmas have been added and/or deleted from the index. """
		c = sqlite3.connect(self.filename)
		c.execute('analyze')
		c.commit()
		c.close()

	def remove_index(self):
		""" Remove the index from the filesystem. """
		try:
			os.remove(self.filename)
			self.index_created = False
		except OSError, (errno, message):
			if errno==2:
				raise FastSSException('Index not found', 'index_not_found')
			else:
				raise

	def search(self, query, max_distance, nocase=False, show_user_fields=False):
		""" Search in the index for the query string, returning all lemmas
		whose edit distance is equal or smaller than max_distance. If nocase is True
		searches are case-insensitive. If show_user_fields is True the user_fields
		associated with each lemma will also be returned. """

		depth = min((max_distance, len(query)))
		if not self.index_created:
			raise FastSSException("Index not created yet", "index_not_created_yet")
		c = sqlite3.connect(self.filename)
		c.create_function('ed_dls', 2, lambda dls1, dls2: _ed(_parse_deletion_list_string(dls1),
										 _parse_deletion_list_string(dls2)))

		temp_table_name = 'query_neighbourhood_%s' % uuid.uuid1().hex
		c.execute('''create temp table %s(
					fragment text not null,
					deletion_sequence blob not null,
					total_deletions integer)''' % temp_table_name)
		# There is no need to decide whether to create an index for the
		# temporary table as sqlite3 will automatically create a temporary
		# table if it is advantageous for the search to be carried out.
		c.executemany('''insert into %s (fragment, deletion_sequence, total_deletions)
						values (?, ?, ?)''' % temp_table_name,
						_wrap_fastss_generator(_delneigh(query, depth)))

		hits = c.execute('''select lemmas.lemma,
				min(ed_dls(tt.deletion_sequence, fragments.deletion_sequence)) as med
				%s
				from lemmas
				join fragments
					on lemmas.lemma_id = fragments.lemma_id
				join %s as tt 
					on tt.fragment = fragments.fragment %s
						and tt.total_deletions<=? 
						and fragments.total_deletions<=?
				group by lemmas.lemma
				having med <= ?
				order by med, lemmas.lemma''' % (',lemmas.user_field' if show_user_fields else '',
								 temp_table_name,'collate nocase' if nocase else ''),
				(max_distance,max_distance,max_distance))

		for hit in hits: yield hit
		c.commit()
		c.close()

	
			
#####


def _ed(delx, dely):

	distance = 0
	while 1:
		if not dely:
			return distance+len(delx)
		elif not delx:
			return distance+len(dely)
		elif delx[0]<dely[0]:
			distance+=1
			delx=delx[1:]
			continue
		elif delx[0]>dely[0]:
			distance+=1
		else:
			distance+=1
			delx=delx[1:]
		dely=dely[1:]


class FastSSException(Exception):
	def __init__(self, message, type):
		Exception.__init__(Exception(message))
		self.type = type

def _delneigh(s, depth):
	if depth>len(s): raise FastSSException('Deletion depth should be smaller than the length of the string.', 'large_depth')
	sl = [char for char in s]
	delseqs = itertools.chain(*(itertools.combinations(tuple(range(len(s))), cd) for cd in xrange(depth+1)))
	cache = {():sl}
	delseqs.next()
	yield [u''.join(s), (), 0]
	for delseq in delseqs:
		lendelseq = len(delseq)
		delseq = tuple([pair[0]-pair[1] for pair in zip(delseq,xrange(len(delseq)))])
# Build reduced string.
		#if lendelseq==1:
		start_str = copy.copy(cache[delseq[:-1]])
		start_str.pop(delseq[-1])
		cache[delseq]=start_str
		yield [u''.join(start_str), delseq, lendelseq]

def _wrap_fastss_generator(gen):
	for triple in gen:
		triple[1] = buffer(cPickle.dumps(triple[1], cPickle.HIGHEST_PROTOCOL))
		yield triple

def _parse_deletion_list_string(dls):
	return cPickle.loads(dls.__str__())
