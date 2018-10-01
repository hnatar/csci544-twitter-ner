#!/usr/bin/env/python

"""
Initial idea:
	Gazettes are said to be useful for identifying Named Entities,
	I load some of the provided lexicons into a trie structure so that
	the presence of a query word in them can be found in O ( len(word) )

	I initially tried to roll my own trie implementation using Python dicts,
	but it was naive / had very bad complexity.

	I've used a library called MARISA Trie (Matching Algorithm with Recursively Implemented StorAge)
	The C++ version: [https://github.com/s-yata/marisa-trie]
	Python : [https://github.com/pytries/marisa-trie] (used)
	This makes building and loading the tries almost instant on my laptop.

	I hope this is ok, since the functionality provided by the library is just
	that of a generic (very fast!) trie.

	Running this file with 'python gentries.py' should generate all the
	tries that I've used. Please ensure that the directory structure is
	as follows:

	. . .
	  |__ gentries.py
	  |__ data/
	  	 |__ lexicon/
	  	 |  |__ location
	  	 |  |__ people.person
	  	 |__ tries/
	  	 |  |__ location.trie (will get generated)
	  	 |  |__ person.trie
	  	 | 
	   . . .

    The major issue with how good these are as features is that, especially on Twitter,
    people do not spell things / write them properly. Any slight change to an entity
    will show up as not being in the trie. Other data structures which allow a search
    for strings within some Levenshtein distance may be useful.
"""

import cPickle as pickle
import string
import marisa_trie

def LoadTrieFromFile(path):
	r = None
	print "Reading trie from file '%s'" % path
	with open(path, 'rb') as f:
		r = pickle.load(f)
		f.close()
	return r

def gen_exact_trie(lexicon):
	tmp = []
	tmp_lower = []
	name = lexicon + '_exact'
	name_lower = name + '_lower.trie'
	name += '.trie'
	with open('data/lexicon/' + lexicon, 'r') as f:
		for line in f.readlines():
			line = line.strip('\n')
			tmp.append( line )
			tmp_lower.append( line.lower() )
		f.close()
	tmp_trie = marisa_trie.BinaryTrie( tmp )
	with open('data/tries/' + name, 'wb') as f:
		pickle.dump(tmp_trie, f, -1)
		f.close()
	print "Generated 'data/tries/%s'" % name
	tmp_trie = marisa_trie.BinaryTrie( tmp_lower )
	with open('data/tries/' + name_lower, 'wb') as f:
		pickle.dump(tmp_trie, f, -1)
		f.close()
	print "Generated 'data/tries/%s'" % name_lower
	return

def gen_nospace_trie(lexicon):
	tmp = []
	tmp_lower = []
	name = lexicon + '_nospace'
	name_lower = name + '_lower.trie'
	name += '.trie'
	with open('data/lexicon/' + lexicon, 'r') as f:
		for line in f.readlines():
			line = line.strip('\n')
			line = ''.join( line.split() )
			tmp.append( line )
			tmp_lower.append( line.lower() )
		f.close()
	tmp_trie = marisa_trie.BinaryTrie( tmp )
	with open('data/tries/' + name, 'wb') as f:
		pickle.dump(tmp_trie, f, -1)
		f.close()
	print "Generated 'data/tries/%s'" % name
	tmp_trie = marisa_trie.BinaryTrie( tmp_lower )
	with open('data/tries/' + name_lower, 'wb') as f:
		pickle.dump(tmp_trie, f, -1)
		f.close()
	print "Generated 'data/tries/%s'" % name_lower
	return

def gen_abbreviation_trie(lexicon):
	tmp = []
	tmp_lower = []
	name = lexicon + '_abbreviation'
	name_lower = name + '_lower.trie'
	name += '.trie'
	with open('data/lexicon/' + lexicon, 'r') as f:
		for line in f.readlines():
			line = line.strip('\n')
			line = line.split()
			if len(line) == 1:
				continue
			else:
				abbr = ''
				for word in line:
					if word[0] == word[0].upper():
						# should work most of the time
						abbr += word[0]
				tmp.append( abbr )
				tmp_lower.append( abbr.lower() )
		f.close()
	tmp_trie = marisa_trie.BinaryTrie( tmp )
	with open('data/tries/' + name, 'wb') as f:
		pickle.dump(tmp_trie, f, -1)
		f.close()
	print "Generated 'data/tries/%s'" % name
	tmp_trie = marisa_trie.BinaryTrie( tmp_lower )
	with open('data/tries/' + name_lower, 'wb') as f:
		pickle.dump(tmp_trie, f, -1)
		f.close()
	print "Generated 'data/tries/%s'" % name_lower
	return

def gen_chunks_trie(lexicon):
	tmp = []
	tmp_lower = []
	name = lexicon + '_chunks'
	name_lower = name + '_lower.trie'
	name += '.trie'
	with open('data/lexicon/' + lexicon, 'r') as f:
		for line in f.readlines():
			line = line.strip('\n')
			for word in line.split(' '):
				tmp.append( word )
				tmp_lower.append( word.lower() )
		f.close()
	tmp_trie = marisa_trie.BinaryTrie( tmp )
	with open('data/tries/' + name, 'wb') as f:
		pickle.dump(tmp_trie, f, -1)
		f.close()
	print "Generated 'data/tries/%s'" % name
	tmp_trie = marisa_trie.BinaryTrie( tmp_lower )
	with open('data/tries/' + name_lower, 'wb') as f:
		pickle.dump(tmp_trie, f, -1)
		f.close()
	print "Generated 'data/tries/%s'" % name_lower
	return

if __name__ == "__main__":
	"""
	Running this should generate all the tries which are
	needed and place them in data/tries/.

	The tries are built using strings from the lexicons 
	given (person.person, location, etc.)

	Many tries are created for each lexicon: one with the exact
	words as the lexicon entries (capitalization etc.),
	one without any spaces betwen words, one with all letters
	lowercased, one which tries to find "acronyms" if there
	are multiple words, etc. ( please see the gen_(...)_trie functions )

	"""

	# Manually encode and test some strings, to show trie works
	# List of US state abbreviations, from Wikipedia
	states = {'A': 'LKZR',
			  'C': 'AOT',
			  'D': 'CE',
			  'F': 'L',
			  'G': 'AU',
			  'H': 'I',
			  'I': 'DLNA',
			  'K': 'SY',
			  'L': 'A',
			  'M': 'EDAINSOT',
			  'N': 'EVHJMYCD',
			  'O': 'HKR',
			  'P': 'AR',
			  'R': 'I',
			  'S': 'C',
			  'S': 'D',
			  'T': 'NX',
			  'U': 'T',
			  'V': 'TA',
			  'W': 'AVIY'}
	state_list = []
	for first in states:
		for second in states[first]:
			state_list.append( first + second )
	us_state_trie = marisa_trie.BinaryTrie( state_list )
	print state_list
	# save to file
	with open('data/tries/us_state_abbr.trie', 'wb') as f:
		pickle.dump(us_state_trie, f, -1)
		f.close()
	# read and query
	state_trie = LoadTrieFromFile('data/tries/us_state_abbr.trie')
	for test in ["CA", "LA", "TX", "TN", "NYC", "HO", "ca"]:
		print test, test in state_trie


	"""
	Generate the tries actually used as features
	"""
	trie_builders = [ gen_exact_trie, gen_nospace_trie, gen_abbreviation_trie ]
	lexicons = ['architecture.museum', 'automotive.make', 'automotive.model', 'award.award',
				'base.events.festival_series', 'bigdict', 'book.newspaper', 'broadcast.tv_channel',
				'business.brand', 'business.consumer_company', 'business.consumer_product', 'business.sponsor',
				'cap.1000', 'cvg.computer_videogame', 'cvg.cvg_developer', 'cvg.cvg_platform',
				'education.university', 'english.stop', 'firstname.5k', 'government.government_agency',
				'internet.website', 'lastname.5000', 'location', 'location.country', 'people.family_name',
				'people.person', 'people.person.lastnames', 'product', 'sports.sports_league', 'sports.sports_team',
				'time.holiday', 'time.recurring_event', 'transportation.road', 'tv.tv_network', 'tv.tv_program',
				'venture_capital.venture_funded_company', 'venues']
	for lex in lexicons:
		gen_exact_trie(lex)
		gen_nospace_trie(lex)
		gen_abbreviation_trie(lex)
		gen_chunks_trie(lex)



















