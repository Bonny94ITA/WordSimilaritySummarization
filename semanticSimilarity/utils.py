import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus.reader.wordnet import Lemma
from nltk import word_tokenize


# Lettura file
def read_file(path):
    array = []
    with open(path, "r") as tsv:
        for line in tsv:
            array.append(line)
    return array


# Pulizia del file letto
def extract_word(array):
    words_pair = []
    for elem in array[200:400]:
        tmp = re.split(r'\t+', elem.rstrip('\t'))
        tmp[2] = tmp[2].rstrip('\n')
        words_pair.append(tmp)
    return words_pair


# Media
def means(eval_uno, eval_due):
    return (int(eval_uno) + int(eval_due)) / 2


# Scrittura file output
def write_output(eval_uno, eval_due, correlation):
    with open("./asset/output.txt", "w") as tsv:
        for uno, due in zip(eval_uno, eval_due):
            tsv.write(
                uno[0] + " " + uno[1] + " " + uno[2] + " " + due[2] + " " + str(means(uno[2], due[2])) + "\n")
        tsv.write("Correlation Pearson: " + str(correlation[0][1].iat[0, 1]))
