import nltk
import urllib
import urllib3
import json
import csv
from nltk.corpus import stopwords
from nltk import word_tokenize
from itertools import zip_longest
from gensim.summarization import keywords

stop_words = set(stopwords.words('english'))
stop_words.add(',')
stop_words.add('.')
stop_words.add(';')
stop_words.add(':')
stop_words.add('-')
stop_words.add('*')
stop_words.add('(')
stop_words.add(')')
stop_words.add('[')
stop_words.add(']')
stop_words.add('{')
stop_words.add('}')
stop_words.add('\'')
stop_words.add('\"')
stop_words.add('’')
stop_words.add('“')
stop_words.add('”')
stop_words.add('Mr.')
stop_words.add('etc')
stop_words.add("'s")
stop_words.add("Lt.")
stop_words.add("n't")
stop_words.add("That")
stop_words.add("Are")
stop_words.add("Is")

# Parole o pezzi di frasi che si possono trovare all'interno di frasi importanti in un testo
bonus = ['the main aim', 'the purpose', 'in this report', 'outline', 'our investigation has shown that',
         'finally', 'certainly', 'completely', 'decisively', 'definitely', 'permanently', 'lastly', 'assuredly',
         'beyond recall', 'beyond shadow of doubt', 'conclusively', 'for ever', 'for good', 'in conclusion',
         'inescapably', 'inexorably', 'irrevocably', 'once and for all', 'past regret', 'with conviction',
         'absolutely', 'assuredly', 'exactly', 'surely', 'clearly', 'beyond any doubt', 'categorically',
         'doubtlessly', 'explicitly', 'expressly', 'far and away', 'indubitably', 'no ifs ands or buts about it',
         'positively', 'specifically', 'unmistakably', 'without doubt', 'without fail', 'without question',
         'the documentary opens', 'also caused', 'statements', 'news', 'lower', 'higher', 'greater', 'most', 'many',
         'more', 'much', 'better', 'best', 'partially', 'slightly', 'somewhat', 'at best', 'at most', 'bit by bit',
         'by degrees', 'halfway', 'in a general way', 'in bits and pieces', 'in part', 'in some measure', 'main',
         'expectations', 'driven by', 'suggested that', 'the decisive factor', 'the big question raised',
         'there is one thing', 'the final', 'a challenge', 'we are led to imagine', 'brought out', 'important part',
         'showing', 'the first', 'once again reminds us', 'important', 'principal']


# Estrazione del synset/senso da babelnet.io
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

    print(lemma)
    print(response)
    print(babel_synset)

    return ['BABEL SYNSET NOT FOUND'] if 'message' in babel_synset else babel_synset


# Lettura file da testare (es. Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt)
def read_file(path):
    array = []
    with open(path, "r", encoding='utf8') as tsv:
        for line in tsv:
            array.append(line)
    return array[4:]


# Lettura file synset.txt
def read_file_synset(path):
    array = []
    with open(path, "r") as tsv:
        for line in tsv:
            array.append(line)
    return array


# Lettura file dd-nasari.txt
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


# Dizionario con parola come chiave e babel synset id come valore
def word_to_synset_dict(babel_synsets):
    word_2_babel = dict()

    for bab_syn in babel_synsets:
        if bab_syn[0] == '#':
            key = bab_syn[1:-1]
            word_2_babel[key] = []
        else:
            if (len(word_2_babel[
                        key]) < 15):  # NUMERO DI BABEL SYNSET DA PRENDERE IN CONSIDERAZIONE NEL FILE synsets.txt
                word_2_babel[key].append(bab_syn[:-1])
    return word_2_babel


# Individuazione delle 10 keywords più presenti nel testo grazie alla libreria gensim
def get_key_words(text):
    new_text = ""
    for sent in text:
        new_text += sent
    return keywords(new_text, words=10).split("\n")


# Inizializzazione dizionario per small nasari per separare lemma e peso
def nasari_lemma_peso(lemma, peso):
    return lemma


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
            dictionary["Paragrafi"].append(elem.rstrip('\n'))
    return dictionary


########## PULIZIA TITOLO ##########


# Per verificare se una parola è un nome proprio controllo:
# - se la prima lettera è maiuscola
# - se la parola è un nome (PoS = NN)
def check_proper_noun(word):
    # controllo il pos tag della parola sia in minuscolo che maiuscolo per capire se è un nome;
    # "Is" ad esempio è mostrato come nome mentre è un verbo, per questo si controlla che sia effetivamente un NN
    # anche quando è minuscolo
    return word[0].isupper() and nltk.pos_tag([word.lower()])[0][1] == "NN"  # and len(wn.synsets(word)) == 0


# Controllo se la parola è presente nella frase
def check_in_sentence(word, sentence):
    for w in sentence:
        if word == w or word in w:
            return True
    return False


# Uniamo i nomi propri all'interno di frasi in un'unica parola
def unify_name(sentence):
    sentence_word = []
    for i, word in enumerate(sentence):
        check = check_in_sentence(word, sentence_word)
        if check_proper_noun(word) and not check:
            w = word
            for word1 in sentence[i + 1:]:
                if check_proper_noun(word1):
                    w += " " + word1
                else:
                    break
            sentence_word.append(w)
        else:
            if not check:
                sentence_word.append(word)
    return sentence_word


# Eliminazione delle stop word (es. and, at, etc...)
def delete_stop_words(word_tokens):
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
    return filtered_sentence


# Pulizia del titolo con unione dei nomi propri in unico token ed eliminazione delle stop words
def clean_title(dictionary):
    unified = unify_name(dictionary["Titolo"])
    dictionary["Titolo"] = delete_stop_words(unified)
    return dictionary


########## FINE PULIZIA TITOLO ##########


# Raggruppa dati in chunk di lunghezza fissa. Se mancano dati per formare il chunk prende gli elementi prima per formarlo
# es. grouper('ABCDEFG', 3) --> ABC DEF GEF
def grouper(iterable, n, fillvalue=None):
    resto = len(iterable) % n
    if resto != 0:
        iterable += iterable[-n:-resto]
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def generate_summary(summary):
    summary.sort(key=lambda x: x[2])
    text_summary = ""
    for paragraph in summary:
        paragraph[1].sort(key=lambda x: x[2])
        for sentence in paragraph[1]:
            text_summary += sentence[1] + " "
        text_summary += "\n\n"
    return text_summary


# Salvataggio su file del riassunto
def save_summary(summary):
    with open("./asset/summary.txt", "w", encoding='utf8') as output:
        # with open("./asset/summary_trivial.txt", "w", encoding='utf8') as output:
        output.write(generate_summary(summary))
