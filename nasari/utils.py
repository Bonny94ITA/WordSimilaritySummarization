from nltk.corpus import stopwords
from nltk import word_tokenize
import math

stop_words = set(stopwords.words('english'))
stop_words.add(',')
stop_words.add('.')
stop_words.add(';')
stop_words.add(':')
stop_words.add('(')
stop_words.add(')')
stop_words.add('\'')
stop_words.add('\"')
stop_words.add('’')
stop_words.add('“')
stop_words.add('”')
stop_words.add('Mr.')
stop_words.add('etc')
stop_words.add("'s")
stop_words.add("Lt.")


# Lettura file
def read_file(path):
    array = []
    with open(path, "r", encoding='utf8') as tsv:
        for line in tsv:
            array.append(line)
    return array[4:]


# Inizializzazione dizionario
def init_dictionary():
    dictionary = {"Titolo": "", "Paragrafi": []}
    return dictionary


# Divisione del testo in titolo e paragrafi
def paragraph(text):
    dictionary = init_dictionary()
    dictionary["Titolo"] = text[0].rstrip('\n')
    for elem in text[2:]:
        if elem != "\n":
            dictionary["Paragrafi"].append(elem.rstrip('\n'))
    return dictionary


# Eliminazione delle stop word (es. and, at, etc...)
def delete_stop_words(sentence):
    word_tokens = word_tokenize(sentence)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence
