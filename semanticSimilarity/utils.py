import re
import numpy as np
import urllib
import urllib3
import json


########## SEMANTIC SIMILARITY ##########


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
        values = re.split(r'\t+', elem.rstrip('\t'))  # le due parole con il numero annotato
        values[2] = values[2].rstrip('\n')  # cancelliamo lo \n dall'ultimo elemento
        words_pair.append(values)

    return words_pair


# Media
def means(eval_uno, eval_due):
    return (int(eval_uno) + int(eval_due)) / 2


# Scrittura del file output
def write_output(eval_uno, eval_due, correlation):
    with open("./asset/output.txt", "w") as tsv:
        for jack, tommy in zip(eval_uno, eval_due):  # word1 \t word2 valjack valtommy mediaval
            tsv.write(
                jack[0] + "\t" + jack[1] + "\t" + jack[2] + "\t" + tommy[2] + "\t" + str(
                    means(jack[2], tommy[2])) + "\n")
        tsv.write("Correlation Pearson: " + str(correlation[0][1].iat[0, 1]))


########## FINE SEMANTIC SIMILARITY ##########

########## SENSE IDENTIFICATION ##########


# Dizionario con parola come chiave e babel synset id come valore
def word_to_babel_dict(babel_synsets):
    word_2_babel = dict()

    for bab_syn in babel_synsets:
        if bab_syn[0] == '#':
            key = bab_syn[1:-1]
            word_2_babel[key] = []
        else:
            word_2_babel[key].append(bab_syn[:-1])
    return word_2_babel


# Dizionario con babel synset come chiave e vettore di descrittori come valore
def babel_to_vector_dict(nasari):
    babel_2_vector = dict()

    for line in nasari:
        values = re.split(r'\t+', line.rstrip('\t'))
        key = re.split('__', values[0].rstrip('__'))[0]
        babel_2_vector[key] = np.array(values[1:], dtype=np.double)

    return babel_2_vector


# Dizionario con chiave tupla di due parole e valore le valutazioni e la medie annotate manualmente
def words_to_eval(evals):
    words_2_eval = dict()

    for line in evals:
        values = re.split(r'\t+', line.rstrip('\t'))
        values[-1] = values[-1].rstrip('\n')
        words_2_eval[(values[0], values[1])] = values[2:]

    return words_2_eval


# Estrazione della glossa da babelnet.io
def get_gloss(id):
    service_url = 'https://babelnet.io/v5/getSynset'
    params = {
        'id': id,
        'key': '9f73a72d-0ad4-4f30-bf46-5249377326cc'
    }

    url = service_url + '?' + urllib.parse.urlencode(params)
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    babel_synset = json.loads(response.data.decode('utf-8'))

    return ['BABEL SYNSET NOT FOUND'] if 'message' in babel_synset else babel_synset['glosses'][0]['gloss']


# Scrittura del file babs_and_gloss_evaluation con la glossa estratta
def write_words_and_babs(words_and_babs):
    with open("./asset/babs_and_gloss.txt", "w") as tsv:
        for word_bab in words_and_babs:
            if word_bab[1] is not None:
                # tsv.write(word_bab[0][0]+" "+word_bab[0][1]+"\n"+word_bab[1][0]+"\n"+word_bab[1][1]+"\n\n")
                tsv.write(word_bab[0][0] + " " + word_bab[0][1] + " " + word_bab[1][0] + " " + word_bab[1][
                    1] + "\n" + get_gloss(word_bab[1][0]) + "\n" + get_gloss(word_bab[1][1]) + "\n\n")

########## FINE SENSE IDENTIFICATION ##########
