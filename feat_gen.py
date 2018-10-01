#!/bin/python

import gentries
import string
import nltk
import numpy as np


"""
Using GloVe vectors and dot product to find similar
vectors. Didn't work very well.
(no noticeable change to F1 score on dev_test)

print 'Loading pre-trained GloVe vectors from Tweet corpus ( ~250 MB ) ... ',
glovevec = {}
with open('twitter_glove.txt', 'r') as f:
    for line in f:
        line = line.split()
        word = line[0]
        vector = np.array( [ float(x) for x in line[1:] ] )
        glovevec[word] = vector
    f.close()
print 'Finished.'
cluster = {}
cluster['company'] = ['microsoft', 'twitter', 'nintendo', 'amazon', 'reuters', 'twc', 'pepsi', 'engadget', 'yahoo',
            'playboy', 'facebook', 'gucci', 'walmart', 'ufc', 'youtube','skype','marlboro','ducati','mcdonalds']
cluster['facility'] = ['venue','lounge','cafe','club','building','centre','park','bridge','airport','bar','campus',
            'studio','house','university','cathedral','mansion','school','field','gallery','pub','museum']
cluster['geoloc'] = ['ga','vancouver','scotland','belgium','greenville','ohio','gainesville','singapore','india','ny',
            'london','hawaii','houston','canada','denver','austin','paris','japan','uk','sydney','maryland',
            'america','ca']
cluster['sports'] = ['dodgers','lancers','wolves','lions','wildcats','boilers','vikings','blackhawks','jets','madrid',
          'barcelona','yankees','lakers','atletico','india','pakistan','australia','coach','cup','trophy','lakers','clippers']

def glove_tags(word):
    if word not in glovevec:
        return []
    avg = 0.0
    best_cluster_tag = None
    best_cluster_avg = None
    r = []
    for k in cluster:
        avg = 0.0
        for node in cluster[k]:
            avg += np.dot(np.linalg.norm(glovevec[word]), np.linalg.norm(glovevec[node]))
        avg /= float(len(cluster[k]))
        if best_cluster_tag == None or avg > best_cluster_avg:
            best_cluster_avg = avg
            best_cluster_tag = 'BEST_CLUSTER_' + k
        if avg > 0.8:
            r.append('MEMBER_OF_'+k)
    r.append(best_cluster_tag)
    return r
"""


"""
Using presence in various Gazettes as features
(please also see gentries.py for generation/loading)
"""
lexicons = ['architecture.museum', 'automotive.make', 'automotive.model', 'award.award',
            'base.events.festival_series', 'book.newspaper', 'broadcast.tv_channel',
            'business.brand', 'business.consumer_company', 'business.consumer_product', 'business.sponsor',
            'cap.1000', 'cvg.computer_videogame', 'cvg.cvg_developer', 'cvg.cvg_platform',
            'education.university', 'english.stop', 'firstname.5k', 'government.government_agency',
            'internet.website', 'lastname.5000', 'location', 'location.country', 'people.family_name',
            'people.person', 'people.person.lastnames', 'product', 'sports.sports_league', 'sports.sports_team',
            'time.holiday', 'time.recurring_event', 'transportation.road', 'tv.tv_network', 'tv.tv_program',
            'venture_capital.venture_funded_company', 'venues']

TrieStr2Trie = {}
for lex in lexicons:
    for ttype in ['exact', 'nospace', 'abbreviation', 'chunks']:
        TrieStr2Trie[lex+'_'+ttype] = gentries.LoadTrieFromFile('data/tries/'+lex+'_'+ttype+'.trie')
        TrieStr2Trie[lex+'_'+ttype+'_lower'] = gentries.LoadTrieFromFile('data/tries/'+lex+'_'+ttype+'_lower.trie')

def tag_with_tries(word):
    """
    Called to add features to a word based on the lexicons it is
    a member of. Being a "member" can mean that there is an exact
    match, or that there are keys in the trie for which this word
    is a prefix.

    The lexicons/tries are basically the same data, stored in different
    pre-processed ways for each of the provided lexicons in data/lexicons.
    (please see gentries.py)
    """
    tags = []
    rettags = []
    if word[0] == '#':
        word = word[1:]
        # Need this for an index error
        if not word:
            word = ' '
    # Adding this finally pushed macro F1 over 20
    if word.lower() in TrieStr2Trie['english.stop_exact']:
        rettags.append('STOP_WORD')
    # If exact matches are found in lexicons, prefer them
    # to partial matches in others. Same for being a properly
    # shaped prefix of an exact entry.
    found_exact = False
    for trie in TrieStr2Trie:
        if 'exact' in trie:
            if TrieStr2Trie[trie].has_keys_with_prefix(word):
                found_exact = True
                if word in TrieStr2Trie[trie]:
                   rettags.append('EXACT_MATCH_' + trie)
                else:
                   rettags.append('EXACT_PREFIX_MATCH_' + trie)
    # try matching for chunks
    found_chunk = False
    if (not found_exact):
        for trie in TrieStr2Trie:
            if 'chunk' in trie:
                if TrieStr2Trie[trie].has_keys_with_prefix(word):
                    found_chunk = True
                    tags.append('CHUNK_MATCH'+trie)
    # nothing worked
    found_r = False
    if (not found_exact) and (not found_chunk):
        matches = 0
        for trie in TrieStr2Trie:
            if 'exact' in trie or 'chunk' in trie:
                continue
            if 'lower' in trie and TrieStr2Trie[trie].has_keys_with_prefix(word.lower()):
                tags.append(trie)
                found_r = True
                if word.lower() in TrieStr2Trie[trie]:
                    tags.append('POSSIBLE_NE'+trie)
                else:
                    tags.append('POSSIBLE_NE_PREFIX'+trie)
            if 'abbreviation' in trie and TrieStr2Trie[trie].has_keys_with_prefix(word):
                tags.append(trie)
                if word in TrieStr2Trie[trie]:
                    tags.append('POSSIBLE_NE'+trie)
    # the potential tags are assigned based off of 'intuition',
    # not something rigorous
    for tag in tags:
        for area in ['business.brand','business.consumer_company', 'cvg_developer', 'venture', 'newspaper']:
            if area in tag:
                rettags.append('COMPANY')
        for area in ['university', 'venues','location','location.country']:
            if area in tag:
                rettags.append('GEOLOC')
        for area in ['person','firstname','lastname']:
            if area in tag:
                rettags.append('PERSON')
            if 'firstname' in tag:
                rettags.append('BPERSON')
            else:
                rettags.append('IPERSON')
        for area in ['product','automotive','consumer_product','computer_videogame','cvg_platform']:
            if area in tag:
                rettags.append('PRODUCT')
        for area in ['sports']:
            if area in tag:
                rettags.append('SPORTS')
        for area in ['tv','broadcast']:
            if area in tag:
                rettags.append('TV')
        for area in ['award','festival','government','transportation','website']:
            if area in tag:
                rettags.append('OTHER')
    return rettags

"""
This was the easiest place to put this, during the training phase,
it tries to find the Penn Treebank tag for common words like 'at', 'the', 'in', etc.
Then, during feature addition, if the word has been tagged with a Penn POS tag before,
the tag is added as a feature. This map stores words which have been tagged.

No verbs, nouns, adjectives, etc. are tagged here. Just what I consider to be 'rigid'
in their semantics.
"""
NLTK_pos_tags = {}
def preprocess_corpus(train_sents):
    for sent in train_sents:
        for word in sent:
            if word in NLTK_pos_tags:
                continue
            word_tag = nltk.pos_tag(word)[0][1]
            if word_tag in ['CC', 'DT', 'IN', 'PDT', 'POS', 'TO']:
                NLTK_pos_tags[word] = word_tag


def token2features(sent, i, add_neighs = True):
    """Compute the features of a token."""
    """ (mine are below ) """
    ftrs = []
    # bias
    ftrs.append("BIAS")
    # position features
    if i == 0:
        ftrs.append("SENT_BEGIN")
    if i == len(sent)-1:
        ftrs.append("SENT_END")
    # the word itself
    word = unicode(sent[i])
    ftrs.append("WORD=" + word)
    # removed because it caused overfitting
    # feature below captures much of the same info I think
    ftrs.append("LCASE=" + word.lower())
    # some features of the word
    if word.isalnum():
        ftrs.append("IS_ALNUM")
    if word.isnumeric():
        ftrs.append("IS_NUMERIC")
    if word.isupper():
        ftrs.append("IS_UPPER")
    if word.islower():
        ftrs.append("IS_LOWER")
    if word.isdigit():
        ftrs.append("IS_DIGIT")
    # previous/next word feats
    if add_neighs:
        if i > 0:
            for pf in token2features(sent, i-1, add_neighs = False):
                ftrs.append("PREV_" + pf)
        if i < len(sent)-1:
            for pf in token2features(sent, i+1, add_neighs = False):
                ftrs.append("NEXT_" + pf)
    """ MY FEATURES """

    # --- hashtag and handles
    # (tried to add features identifying these, negligible change.
    #  so just trim the symbol here)
    if word[0] in '#':
        word = word[1:]
        if not word:
            return ftrs
    
    """
    # --- clustering with GloVe Tweet corpus
    (scrapped, no change)
    gt = glove_tags(word)
    if not gt == []:
        ftrs.extend(gt)
    """

    # --- selectively tag using tries
    ftrs.extend(tag_with_tries(word.encode('utf-8')))

    # --- word shape
    # captial letters -> A, small ones -> a, punctuation -> .
    # improves f1 score a bit
    shape = ''
    if word[0] in string.ascii_lowercase:
        shape_type = 0 # lowercase
        shape = 'a'
    elif word[0] in string.ascii_uppercase:
        shape_type = 1 # uppercase
        shape = 'A'
    elif word[0] in '0123456789':
        shape_type = 3
        shape = 'd'
    else:
        shape_type = 2
        shape = '.'
    for i in range(1, len(word)):
        if shape_type != 0 and word[i] in string.ascii_lowercase:
            shape += 'a'
            shape_type = 0
        elif shape_type != 1 and word[i] in string.ascii_uppercase:
            shape += 'A'
            shape_type = 1
        elif shape_type != 2 and word[i] in string.punctuation:
            shape += '.'
            shape_type = 2
        elif shape_type != 3 and word[i] in '0123456789':
            shape += 'd'
            shape_type = 3
    ftrs.append('SHAPE='+shape)

    # --- NLTK POS tags (specific, simple words only, map during preprocess)
    if word in NLTK_pos_tags:
        ftrs.append('PENN_POS_TAG_' + NLTK_pos_tags[word])

    """ END OF MY FEATURES """
    # cast just in case
    return list(set(ftrs))

if __name__ == "__main__":
    sents = [
    [ "I", "love", "food" ]
    ]
    preprocess_corpus(sents)
    for sent in sents:
        for i in xrange(len(sent)):
            print sent[i], ":", token2features(sent, i)
