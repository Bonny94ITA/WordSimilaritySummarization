import utils


def similarity(vect1, vect2):
    set1 = set(vect1)
    set2 = set(vect2)
    return len(vect1.intersection(vect2))


# Trova la similarità massima dei significati tra le due parole
# calcolando la cosine similarity tra le coppie dei significati
# rappresentati dai vettori di 300 dimensioni (babel_2_vector)
def compute_similarity(babel_ids1, babel_ids2, nasari):
    max_sim = 0.0
    best_bab = None

    for bab1 in babel_ids1:
        for bab2 in babel_ids2:
            vect1 = nasari.get(bab1)  # Estraiamo il vettore per ogni babel synset id
            vect2 = nasari.get(bab2)
            if vect1 is not None and vect2 is not None:
                sim = similarity(vect1["vect"], vect2["vect"])
                if sim > max_sim:
                    max_sim = sim
                    best_bab = (bab1, bab2)
    return max_sim, best_bab


def get_context(title, word_to_synset, nasari):
    for word_uno in title:
        for word_due in title[1:]:
            babel_ids1 = word_to_synset[word_uno]  # estraiamo i significati delle parole
            babel_ids2 = word_to_synset[word_due]
            sim, best_bab = compute_similarity(babel_ids1, babel_ids2, nasari)

    return


def main():
    path = "./asset/Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt"
    # path = "./asset/People-Arent-Upgrading-Smartphones-as-Quickly-and-That-Is-Bad-for-Apple.txt"
    # path = "./asset/The-Last-Man-on-the-Moon--Eugene-Cernan-gives-a-compelling-account.txt"
    path_synsets = "./asset/synsets.txt"
    path_nasari = "./asset/dd-small-nasari-15.txt"

    synsets = utils.read_file_synset(path_synsets)
    word_to_synset = utils.word_to_synset_dict(synsets)

    nasari = utils.read_file_nasari(path_nasari)

    text = utils.read_file(path)
    dictionary = utils.paragraph(text)
    title = utils.delete_stop_words(dictionary["Titolo"])

    # get_context(title, word_to_synset, nasari)


if __name__ == '__main__':
    main()
