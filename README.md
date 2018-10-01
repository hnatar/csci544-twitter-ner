**Note:** Readme from original submission.

# Readme

1. pip install marisa-trie
2. python gentries.py (after placing next to data/)
3. python main.py -T <...> <...>

# Extended

Resources used: 
1) Provided lexicons:
	I used loaded almost all of the provided lexicons into tries,
	and saved them to disk using pickle. At first I tried to write
	my own trie structure, but this was slow. I used the MarisaTrie
	library, which can be installed with:

		pip install marisa-trie

		link: https://github.com/pytries/marisa-trie

	The tries must be present before the feature generation phase,
	and this can be done by running gentries.py (one time thing)

		python gentries.py

	(gentries.py must be placed in same folder as the data/ folder,
	 with the lexicons inside data/lexicons/. The tries are placed
	 into data/tries/.. The data/tries/ folder might have to be created.)

2) GloVe word embeddings:
	https://nlp.stanford.edu/projects/glove/
	I tried to use the GloVe pretrained word embeddings from their
	Twitter corpus to perform word clustering. e.g. I went through the many
	words classified as "company" in the training set. During feature generation,
	for the given word, I took the cosine similarity (averaged) for the given
	word with each of the words in this "company" list. I then tagged the "best"
	cluster for (company, or geoloc, etc.) along with all the clusters with > 0.8
	similarity for a given word. If the word didn't have a GloVe embedding, it was
	ignored.

	( This did not improve F1 at the time, so I ended up not including it during
	my submit. I think I must have done something wrong. The code is in feat_gen.py,
	but commented out. )
