import utils
import pandas as pd
import numpy as np
from nltk import word_tokenize
from nltk.corpus import wordnet as wn


# Calcolo delle correlazioni con Pearson e Spearman
def compute_correlations(correlations):
    df = pd.DataFrame(correlations)
    corrs = [["Pearson", df.corr()]]
    return corrs


# Inizializzazione dizionario (WP = Wu_Palmer, SP = Shortest_Path, LC = Leacock_Chodorow)
def init_annotation(eval_uno, eval_due):
    matrix_uno = np.array(eval_uno).transpose()
    matrix_due = np.array(eval_due).transpose()
    annotation = {"Annotation_Uno": matrix_uno[2].astype(int), "Annotation_Due": matrix_due[2].astype(int)}
    return annotation


def means(eval_uno, eval_due):
    return (eval_uno + eval_due) / 2


def write_output(eval_uno, eval_due, correlation):
    with open("./asset/output.txt", "w") as tsv:
        for uno, due in zip(eval_uno, eval_due):
            tsv.write(uno[0] + " " + uno[1] + " " + uno[2] + " " + due[2] + " " + str(means(int(uno[2]), int(due[2]))) + "\n")
        tsv.write(correlation[0][1][5])


def main():
    path_uno = "./asset/bonazzi.it.test.data.txt"
    path_due = "./asset/toscano.it.test.data.txt"
    reading_uno = utils.read_file(path_uno)
    reading_due = utils.read_file(path_due)
    eval_uno = utils.extract_word(reading_uno)
    eval_due = utils.extract_word(reading_due)
    annotation = init_annotation(eval_uno, eval_due)
    correlation = compute_correlations(annotation)
    print(correlation)
    write_output(eval_uno, eval_due, correlation)

    # print(means(eval_uno, eval_due))


if __name__ == '__main__':
    main()
