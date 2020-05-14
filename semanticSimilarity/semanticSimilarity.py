import utils
import pandas as pd
import numpy as np


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


# Prende i punteggi di entrambi e calcola la correlazione
def main():
    path_uno = "./asset/bonazzi.it.test.data.txt"
    path_due = "./asset/toscano.it.test.data.txt"
    reading_uno = utils.read_file(path_uno)
    reading_due = utils.read_file(path_due)
    eval_uno = utils.extract_word(reading_uno)
    eval_due = utils.extract_word(reading_due)
    correlation = compute_correlations(init_annotation(eval_uno, eval_due))
    utils.write_output(eval_uno, eval_due, correlation)
    print(correlation)


if __name__ == '__main__':
    main()
