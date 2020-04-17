from nltk.corpus import stopwords
from nltk import word_tokenize
import urllib
import urllib3
import json
import csv

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


# Lettura file
def read_file_synset(path):
    array = []
    with open(path, "r") as tsv:
        for line in tsv:
            array.append(line)
    return array


def read_file_nasari(path):
    sense_to_vector = {}
    with open(path, encoding='utf8') as tsv:
        for line in csv.reader(tsv, dialect="excel-tab"):
            result = [x.strip() for x in line[0].split(';')]  # Prelevo un vettore

            # Prelevo il babel synset id
            sense = result[0]
            # Prelevo tutte le parole senza '_' (alcuni vettori hanno più parole + qualche refuso) (non considero la stringa vuota)
            lemma = [x.lower() for x in result[1:] if '_' not in x if x]
            # Prelevo ogni elemento (x) dalla coda del vettore e separo l'elemento (x) tra il lemma e il peso
            vettore = [nasari_lemma_peso(*x.split('_')) for x in result[1:] if x if '_' in x]

            sense_to_vector[sense] = {
                'lemma': lemma,
                'vect': vettore
            }

    return sense_to_vector


# Inizializzazione dizionario per small nasari per separare lemma e peso
def nasari_lemma_peso(lemma, peso):
    return lemma
    # return {"Lemma": lemma, "Peso": peso}


# Inizializzazione dizionario
def init_dictionary():
    dictionary = {"Titolo": "", "Paragrafi": []}
    return dictionary


# Divisione del testo in titolo e paragrafi
def paragraph(text):
    dictionary = init_dictionary()
    dictionary["Titolo"] = word_tokenize(text[0].rstrip('\n'))
    for elem in text[2:]:
        if elem != "\n":
            dictionary["Paragrafi"].append(word_tokenize(elem.rstrip('\n')))
    return dictionary

#controllo se la parola è presente nella frase
def check_in_sentence(word, sentence):
    for w in sentence:        
        if word == w or word in w:
            return True

    return False

#Uniamo i nomi propri in un'unica parola
def unify_name(sentence):
    sentence_word = []    
    
    for i, word in enumerate(sentence):
        check = check_in_sentence(word, sentence_word)
                
        if(word[0].isupper() and not check):            
            w=word
            for word1 in sentence[i+1:]:
                if(word1[0].isupper()):
                    w+=" "+word1
                else:
                    break
            
            sentence_word.append(w)            
        else:
            if(not check):
                sentence_word.append(word)

    return sentence_word

# Eliminazione delle stop word (es. and, at, etc...)
def delete_stop_words(word_tokens):
    filtered_sentence = [w for w in word_tokens if not w in stop_words]    

    return filtered_sentence


# Estrazione del senso da babelnet.io
def get_synset(lemma):
    service_url = 'http://babelnet.io/v5/getSynsetIds'
    params = {
        'lemma': lemma,
        'searchLang': 'EN',
        'key': '9f73a72d-0ad4-4f30-bf46-5249377326cc'
    }

    url = service_url + '?' + urllib.parse.urlencode(params)
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    babel_synset = json.loads(response.data.decode('utf-8'))

    return ['BABEL SYNSET NOT FOUND'] if 'message' in babel_synset else babel_synset


# Dizionario con parola come chiave e babel synset id come valore
def word_to_synset_dict(babel_synsets):
    word_2_babel = dict()

    for bab_syn in babel_synsets:
        if bab_syn[0] == '#':
            key = bab_syn[1:-1]
            word_2_babel[key] = []
        else:            
            if(len(word_2_babel[key]) < 5):
                word_2_babel[key].append(bab_syn[:-1])            
    return word_2_babel
