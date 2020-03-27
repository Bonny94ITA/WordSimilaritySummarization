import random
from nltk.corpus import semcor
from nltk.corpus.reader.wordnet import Lemma
from nltk import word_tokenize


def semcor_extraction(sentence_number: int = 50) -> tuple:
    """
    Extracts `sentence_number` sentences from the semcore corpus.
    From each of them extracts also a random noun.
    :return: Returns a tuple (extracted sentences list, extracted nouns list)
    """
    sentences = []
    extracted = []

    for i in range(0, sentence_number):
        elem = list(filter(lambda sentence_tree:
                           isinstance(sentence_tree.label(), Lemma) and
                           sentence_tree[0].label() == "NN", semcor.tagged_sents(tag='both')[i]))                

        if elem:
            lemma = select_lemma(elem).label()
            
            extracted.append(lemma)
            sentence = " ".join(semcor.sents()[i])
            
            sentences.append(removeWord(sentence, lemma.name()))

    return sentences, extracted

def select_lemma(lemmas):    
    right_lemma = False
    
    while(not right_lemma):
        lemma = random.choice(lemmas)
        if("_" not in lemma):
            return lemma

def removeWord(sentence, word):
    tokens = word_tokenize(sentence)
    filtered_sentence = [w for w in tokens if w != word]
    return filtered_sentence