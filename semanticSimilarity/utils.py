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
