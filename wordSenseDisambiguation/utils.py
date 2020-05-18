import random
import nltk
from nltk.corpus import semcor
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus.reader.wordnet import Lemma
from nltk import word_tokenize

stop_words = set(stopwords.words('english'))
stop_words.add(',')
stop_words.add('.')
stop_words.add(';')
stop_words.add(':')
stop_words.add('etc')
stop_words.add("'s")
stop_words.add("Lt.")


# Lettura file
def read_file():
    array = []
    with open("./asset/sentences.txt", "r") as tsv:
        for line in tsv:
            array.append(line)
    array.pop(0)
    return array


# Questo metodo viene utilizzato per il file sentences.txt
# Estrazione delle parole e delle posizioni delle parole tra '**'. Viene estratta anche la parte rimanente della frase
def extract_word(sentences):
    word_sent = []
    for sentence in sentences:
        item = []
        word_tokens = word_tokenize(sentence)
        for i, word in enumerate(word_tokens):
            if len(word) > 4 and word[0] == '*' and word[1] == '*':
                item.append(word[2:len(word) - 2])  # Parola tra gli '**' [0]
                item.append(i)  # La posizione della parola nella frase [1]
        word_tokens.pop(item[1])
        item.append(word_tokens)  # Il resto della frase [2]
        word_sent.append(item)
    return word_sent


# Eliminazione delle stop word (es. and, at, etc...)
def delete_stop_words(word_tokens):
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence


# Part of speech tagging e lemmatizzazione
def pos_tagging_and_lemming(word_tokens):
    word_pos_tag = nltk.pos_tag(word_tokens)
    lemmatizer = WordNetLemmatizer()
    lemming_pos = []

    # La lemmatizzazione può essere migliorata aggiungendo il pos tag
    for words, pos in word_pos_tag:
        lemming_pos.append(lemmatizer.lemmatize(words))  # Lemmatizzazione (forma normale del lemma)
        lemming_pos.append(pos)
    return lemming_pos


# Definizione del contesto
def get_context(sentence_tokens):
    return pos_tagging_and_lemming(delete_stop_words(sentence_tokens))


# Ritorna un esempio e la glossa del senso
def get_examples(sense):
    example = sense.examples()
    gloss = sense.definition()
    if len(example) > 0:
        return example[0] + gloss
    else:
        return gloss


# Estrazione di sinonimi random dal senso
def get_synonym(sense):
    return random.choice(sense.lemmas()).name()


# Ricostruisce la frase sostituendo un sinonimo alla parola originale
def rebuild_sentence(sense, sentence_tokens, index):
    synonym = get_synonym(sense)
    sentence = ""

    # Posizioniamo il sinonimo al posto del lemma originale
    # da disambiguare. Per gli altri lemmi aggiungiamo
    # solo uno spazio per ricostruire la frase
    for i, token in enumerate(sentence_tokens):
        if i < index or i > index:
            sentence += token + " "
        else:
            sentence += synonym + " " + token + " "
    return sentence


######################## SEMCOR UTILS ########################


# Seleziona un lemma che abbia una parola singola
def select_lemma(lemmas):
    right_lemma = False
    while not right_lemma:
        lemma = random.choice(lemmas)
        if "_" not in lemma:
            return lemma


# Rimuove la parola scelta dalla frase
def remove_word(sentence, word):
    tokens = word_tokenize(sentence)
    filtered_sentence = [w for w in tokens if w != word]
    return filtered_sentence


# Estrazione 50 frasi con i lemmi sostantivi da semcor
def semcor_extraction(sentence_number=50):
    sentences = []
    extracted = []

    for i in range(0, sentence_number):

        # Estraiamo i nomi dalla frase i
        nouns = list(filter(lambda sentence_tree:
                            isinstance(sentence_tree.label(), Lemma) and
                            sentence_tree[0].label() == "NN", semcor.tagged_sents(tag='both')[i]))

        # Scegliamo un nome a caso della frase dalla lista nouns e lo estraiamo dalla frase i
        if nouns:
            lemma = select_lemma(nouns).label()
            extracted.append(lemma)
            sentence = " ".join(semcor.sents()[i])
            sentences.append(remove_word(sentence, lemma.name()))
    return sentences, extracted
