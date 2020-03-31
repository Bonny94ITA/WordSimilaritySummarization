import metrics
import csv
import pandas as pd
import numpy as np
from nltk.corpus import wordnet as wn

simLabels = ["Means", "WuPalmer", "shortestPath", "LeacockChodorow"]


# Lettura file
def read_file():
    array = []
    with open("./asset/WordSim353.csv") as tsv:
        for line in csv.reader(tsv, delimiter=','):
            array.append(line)
    array.pop(0)
    return array


# Inizializzazione dizionario (WP = Wu_Palmer, SP = Shortest_Path, LC = Leacock_Chodorow)
def init_corr():
    correlations = {"Means": [], "WP": [], "SP": [], "LC": []}
    return correlations


# Estrazione dei synset di WordNet per le coppie di parole del csv
def get_synsets(item):
    return wn.synsets(item[0]), wn.synsets(item[1])


# Calcolo della similarità per ogni metrica: Wu_Palmer, Shortest_Path e Leacock_Chodorow
def compute_similarity(item, metric):
    synset1, synset2 = get_synsets(item)
    max_similarity = 0.0

    for sense1 in synset1:
        for sense2 in synset2:
            similarity = metric(sense1, sense2)

            if similarity is not None:
                if max_similarity < similarity:
                    max_similarity = similarity
    return max_similarity


def print_similarity(correlations, words):
    text = ""
    valuesList = list(correlations.values())
    matrix = np.array(valuesList).transpose()

    for r, row in enumerate(matrix):
        text += words[r][0].upper() + " " + words[r][1].upper() + ":\n"
        for c, col in enumerate(row):
            text += "\t" + simLabels[c] + ": " + str(col) + "\n"
        text += "\n"
    return text + "\n\n"


# Calcolo delle correlazioni con Pearson e Spearman
def compute_correlations(correlations):
    df = pd.DataFrame(correlations)
    corrs = [["Pearson", df.corr()], ["Spearman", df.corr(method='spearman')]]
    return corrs


def print_correlations(corrs):
    text = "CORRELATIONS:\n"
    for cor in corrs:
        text += cor[0] + ": \n" + str(cor[1]) + "\n"
    return text + "\n"


def main():
    array = read_file()
    correlations = init_corr()

    with open("./asset/output.txt", 'w') as outputfile:
        for item in array:
            correlations["WP"].append(compute_similarity(item, metrics.wup_similarity))
            correlations["SP"].append(compute_similarity(item, metrics.shortest_path))
            correlations["LC"].append(compute_similarity(item, metrics.Leacock_Chodorow))
            correlations["Means"].append(float(item[2]))

        outputfile.write(print_similarity(correlations, array))
        corr = compute_correlations(correlations)
        outputfile.write(print_correlations(corr))


if __name__ == '__main__':
    main()
