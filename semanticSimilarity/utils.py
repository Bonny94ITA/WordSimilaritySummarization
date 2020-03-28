import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus.reader.wordnet import Lemma
from nltk import word_tokenize


# Lettura file
def read_file():
    array = []
    with open("./asset/it.test.data.txt", "r") as tsv:
        for line in tsv:
            array.append(line)
    return array


# Pulizia del file letto
def extract_word(array):
    words_pair = []
    for elem in array:
        tmp = re.split(r'\t+', elem.rstrip('\t'))
        tmp[1] = tmp[1].rstrip('\n')
        words_pair.append(tmp)
    return words_pair
