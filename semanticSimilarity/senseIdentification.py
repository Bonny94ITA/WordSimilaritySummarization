import utils
from sklearn.metrics.pairwise import cosine_similarity


# Calcola la cosine similarity
def cosine_simil(vector1, vector2):
    x = vector1.reshape(1, -1)
    y = vector2.reshape(1, -1)

    # Calcolo effetivo della cosine_similarity
    return cosine_similarity(x, y)


# Trova la similarità massima dei significati tra le due parole
# calcolando la cosine similarity tra le coppie dei significati
# rappresentati dai vettori di 300 dimensioni (babel_2_vector)
def compute_similarity(babel_ids1, babel_ids2, babel_2_vector):
    max_sim = 0.0
    best_bab = None

    for bab1 in babel_ids1:
        for bab2 in babel_ids2:
            vect1 = babel_2_vector.get(bab1)  # Estraiamo il vettore per ogni babel synset id
            vect2 = babel_2_vector.get(bab2)
            if vect1 is not None and vect2 is not None:
                sim = cosine_simil(babel_2_vector[bab1], babel_2_vector[bab2])
                if sim > max_sim:
                    max_sim = sim
                    best_bab = (bab1, bab2)
    return best_bab


# Estrae la migliore coppia di sensi per ogni coppia di parole e la scrive su file
def best_senses(words_2_eval, word_2_babel, babel_2_vector):
    words_and_babs = []

    # le chiavi del dizionario words_2_eval sono una tupla con la coppia di parole
    for words in words_2_eval.keys():
        babel_ids1 = word_2_babel[words[0]]  # estraiamo i significati delle parole
        babel_ids2 = word_2_babel[words[1]]
        best_bab = compute_similarity(babel_ids1, babel_ids2, babel_2_vector)
        words_and_babs.append((words, best_bab))

    print(words_and_babs)

    # GUARDARE babs_and_gloss_evaluation.txt

    # Scommentare per riscrivere il file "babs_and_gloss"
    # utils.write_words_and_babs(words_and_babs)


def main():
    path_uno = "./asset/output.txt"
    path_due = "./asset/SemEval17_IT_senses2synsets.txt"
    path_tre = "./asset/mini_NASARI.tsv"
    evals = utils.read_file(path_uno)
    babel_synsets = utils.read_file(path_due)
    nasari = utils.read_file(path_tre)

    # print(nasari)
    words_2_eval = utils.words_to_eval(evals[:-1])
    word_2_babel = utils.word_to_babel_dict(babel_synsets)
    babel_2_vector = utils.babel_to_vector_dict(nasari)
    best_senses(words_2_eval, word_2_babel, babel_2_vector)


if __name__ == '__main__':
    main()
