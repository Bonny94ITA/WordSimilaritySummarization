import nltk
import re
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import semcor as sc
from nltk.corpus import wordnet as wn

stop_words = set(stopwords.words('english'))
stop_words.add(',')
stop_words.add('.')
stop_words.add(';')
stop_words.add(':')
stop_words.add('etc')


# Lettura file
def read_file():
    array = []
    with open("./asset/sentences.txt", "r") as tsv:
        for line in tsv:
            array.append(line)
    array.pop(0)
    return array


def extract_word(tmp):
    pattern = "\*\*"
    items = []
    for elem in tmp:
        item = []
        sentence = str(elem)
        start, end = [x.start() for x in re.finditer(pattern, sentence)]

        begin = sentence[:start]
        final = sentence[end + 2:len(sentence) - 2]
        item.append(sentence[start + 2:end])  # Parola tra gli **
        item.append(begin + final)  # Il resto della frase
        items.append(item)
    return items


# Eliminazione delle stop word (es. and, at, etc...)
def delete_stop_words(sentence):
    word_tokens = word_tokenize(sentence)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return filtered_sentence


# Part of speech tagging e lemmatizzazione
def pos_tagging_and_lemming(tmp):
    word_pos_tag = nltk.pos_tag(tmp)  # Il pos tagging è da gestire ancora meglio per il lemmatizer

    lemmatizer = WordNetLemmatizer()
    lemming_pos = []
    for words, pos in word_pos_tag:
        lemming_pos.append(lemmatizer.lemmatize(words))  # Lemmatizzazione
        lemming_pos.append(pos)
    return lemming_pos


# Definizione del contesto
def get_context(sentence):
    return pos_tagging_and_lemming(delete_stop_words(sentence))


# Ritorna un esempio e la glossa del senso
def get_examples(sense):
    example = sense.examples()
    gloss = sense.definition()
    if len(example) > 0:
        return example[0] + gloss
    else:
        return gloss


def Lesk_algorithm(word, sentence):
    synset = wn.synsets(word)
    best_sense = synset[0]
    max_overlap = 0
    sentence_context = get_context(sentence)
    for sense in synset[1:]:
        signature = get_examples(sense)
        sense_context = get_context(signature)
        print(sense_context)

    print(signature)


def main():
    sentences = read_file()
    tmp = extract_word(sentences)
    # tmp = get_context(tmp[10][1])
    tmp = Lesk_algorithm(tmp[0][0], tmp[0][1])
    print(tmp)


if __name__ == '__main__':
    main()
