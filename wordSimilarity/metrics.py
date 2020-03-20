from nltk.corpus import wordnet as wn
import math

# Calcola la profondità massima di WordNet: 20
MAX_DEPTH = max(max(len(hyp_path) for hyp_path in ss.hypernym_paths()) for ss in wn.all_synsets())


def wup_similarity(synset_x, synset_y):
    # Prendiamo tutti i percorsi che vanno dal senso "entity" (root di wordnet) al senso synset_x
    synset_x_path = synset_x.hypernym_paths()

    # Prendiamo tutti i percorsi che vanno dal senso "entity" (root di wordnet) al senso synset_y
    synset_y_path = synset_y.hypernym_paths()

    # Salviamo in max_synset_x_path il percorso più lungo del synset_x
    for item in synset_x_path:
        if len(item) == max(len(hyp_path) for hyp_path in synset_x_path):
            max_synset_x_path = item

    # Salviamo in max_synset_y_path il percorso più lungo del synset_y
    for item in synset_y_path:
        if len(item) == max(len(hyp_path) for hyp_path in synset_y_path):
            max_synset_y_path = item

    # Per ogni synset 'sense' in max_synset_x_path (partendo da entity) guardo se e è in max_synset_y_path
    for sense in max_synset_x_path:
        if sense in max_synset_y_path:
            lcs = sense

    try:
        # Prendiamo tutti i percorsi che vanno dal senso "entity" (root di wordnet) al senso lcs
        lcs_path = lcs.hypernym_paths()

        # Salviamo in max_lcs_path il percorso più lungo del synset lcs
        for item in lcs_path:
            if len(item) == max(len(hyp_path) for hyp_path in lcs_path):
                max_lcs_path = item

        # Formula di Wu & Palmer
        return (2 * len(max_lcs_path)) / (len(max_synset_x_path) + len(max_synset_y_path))

    except NameError:
        return None


def shortest_path(sense1, sense2):
    minP = sense1.shortest_path_distance(sense2)

    # Formula di Shortest Path
    if minP is None:
        return 0
    else:
        return 2 * MAX_DEPTH - minP


def Leacock_Chodorow(sense1, sense2):
    minP = sense1.shortest_path_distance(sense2)

    # Formula di Leacock & Chodorow
    if minP is None:
        return 0
    else:
        return -math.log((minP + 1) / (2 * MAX_DEPTH + 1))
