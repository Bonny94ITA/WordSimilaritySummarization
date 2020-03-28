import utils
from nltk import word_tokenize
from nltk.corpus import wordnet as wn


def overlap(context1, context2, size):
    olp = 0
    for elem1, elem2 in zip(context1[:size], context2[:size]):
        if elem1 == elem2:
            olp += 1
    return olp


def overlap_intersection(context1, context2, size):
    set1 = set(context1[:size])
    set2 = set(context2[:size])
    return len(set1.intersection(set2))


def max_overlap(context1, context2):
    len1 = len(context1)
    len2 = len(context2)
    olp = 0
    if len1 <= len2:
        olp = overlap_intersection(context1, context2, len1)  # Si può cambiare metodo overlap
    else:
        olp = overlap_intersection(context1, context2, len2)
    return olp


# Algoritmo di Lesk
def Lesk_algorithm(word, sentence_tokens):
    synset = wn.synsets(word)
    best_sense = synset[0]
    max_olp = 0
    sentence_context = utils.get_context(sentence_tokens)

    for sense in synset[1:]:
        sense_examples = utils.get_examples(sense)
        sense_context = utils.get_context(word_tokenize(sense_examples))
        olp = max_overlap(sentence_context, sense_context)
        if max_olp < olp:
            max_olp = olp
            best_sense = sense
    return best_sense


# Accuaratezza Semcor
def compute_accuracy():
    semcor_sentences, semcor_lemmas = utils.semcor_extraction(50)  # Modificare se si vuole un numero diverso di frasi
    corrects = 0

    for sentence, word in zip(semcor_sentences, semcor_lemmas):
        best_sense = Lesk_algorithm(word.name(), sentence)
        if best_sense == word.synset():
            corrects += 1
        print("Sentence: {}\n best_sense: {} real_sense: {}\n\n".format(sentence, best_sense, word.synset()))
    print("Accuracy: ", corrects / len(semcor_lemmas))


def Lesk_test():
    sentences = utils.read_file()
    word_sentences = utils.extract_word(sentences)
    for word_sent in word_sentences:
        best_sense = Lesk_algorithm(word_sent[0], word_sent[2])
        sent = utils.rebuild_sentence(best_sense, word_sent[2], word_sent[1])
        print("Sentence: {}\n sense: {} definition: {}\n\n".format(sent, best_sense, best_sense.definition()))


def main():
    choice = 1

    while choice != "0":
        print("[0] Esci\n[1] Accuracy Semcor\n[2] Lesk_test")
        choice = input("Inserisci numero: \n")
        if choice == "1":
            compute_accuracy()
        elif choice == "2":
            Lesk_test()


if __name__ == '__main__':
    main()
