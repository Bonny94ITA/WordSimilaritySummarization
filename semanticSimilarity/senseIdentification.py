import utils
import pandas as pd
import numpy as np
from nltk import word_tokenize
from nltk.corpus import wordnet as wn
from sklearn.metrics.pairwise import cosine_similarity


# Inizializzazione dizionario per il calcolo della correlazione
def init_annotation(eval_uno, eval_due):
	matrix_uno = np.array(eval_uno).transpose()
	matrix_due = np.array(eval_due).transpose()
	annotation = {"Annotation_Uno": matrix_uno[2].astype(int), "Annotation_Due": matrix_due[2].astype(int)}
	return annotation


# Calcolo delle correlazioni con Pearson e Spearman
def compute_correlations(correlations):
	df = pd.DataFrame(correlations)
	corrs = [["Pearson", df.corr()]]
	return corrs

def cosine_simil(vector1, vector2):	
    x = vector1.reshape(1, -1)
    y = vector2.reshape(1, -1)

    # Now we can compute similarities
    return cosine_similarity(x, y)

def compute_similarity(babel_ids1, babel_ids2, babel_2_vector):
	
	max_sim = 0.0
	best_bab = None

	#print(babel_2_vector.keys())
	for bab1 in babel_ids1:
		for bab2 in babel_ids2:
			#print(bab1, bab2)
			vect1 = babel_2_vector.get(bab1)
			vect2 = babel_2_vector.get(bab2)

			#print(vect1, vect2)
			if(vect1 is not None and vect2 is not None):
				sim = cosine_simil(babel_2_vector[bab1], babel_2_vector[bab2])

				if(sim > max_sim):
					max_sim = sim
					best_bab = (bab1, bab2)

	return best_bab

def best_senses(words_2_eval, word_2_babel, babel_2_vector):

	words_and_babs = []

	for words in words_2_eval.keys():
		babel_ids1 = word_2_babel[words[0]]
		babel_ids2 = word_2_babel[words[1]]

		best_bab = compute_similarity(babel_ids1, babel_ids2, babel_2_vector)

		words_and_babs.append((words, best_bab))

	utils.write_words_and_babs(words_and_babs)

def main():
	path_uno = "./asset/output.txt"
	path_due = "./asset/SemEval17_IT_senses2synsets.txt"
	path_tre = "./asset/mini_NASARI.tsv"
	evals = utils.read_file(path_uno)
	babel_synsets = utils.read_file(path_due)
	nasari = utils.read_file(path_tre)
	
	#print(nasari)
	words_2_eval = utils.words_to_eval(evals[:-1])
	word_2_babel = utils.word_to_babel_dict(babel_synsets)
	babel_2_vector = utils.babel_to_vector_dict(nasari)

	best_senses(words_2_eval, word_2_babel, babel_2_vector)

	#print(word_2_babel)
	#correlation = compute_correlations(init_annotation(eval_uno, eval_due))
	#utils.write_output(eval_uno, eval_due, correlation)
	#print(correlation)


if __name__ == '__main__':
	main()
