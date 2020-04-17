import utils
import itertools
import importlib.util
from nltk import word_tokenize

spec = importlib.util.spec_from_file_location("wordSenseDisambiguation", "../wordSenseDisambiguation/wordSenseDisambiguation.py")
wsb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wsb)

#calcoliamo la similarità con l'intersezione dei termini contenuti nei vettori
def similarity(vect1, vect2):
    set1 = set(vect1)
    set2 = set(vect2)
    return len(set1.intersection(set2))


# Trova la similarità massima dei significati tra le due parole
# calcolando la cosine similarity tra le coppie dei significati
# rappresentati dai vettori di 300 dimensioni (babel_2_vector)
def compute_similarity(bab_id1, bab_id2, nasari):
    #max_sim = 0.0
    #best_bab = None
    sim = 0

    vect1 = nasari.get(bab_id1)  # Estraiamo il vettore per ogni babel synset id
    vect2 = nasari.get(bab_id2)

    #print(vect1)
    #print(vect2)

    if vect1 is not None and vect2 is not None:
        #print("ABBIAMO TROVATO I MINCHIA DI VETTORI")
        sim = similarity(vect1["vect"], vect2["vect"])
        #if sim > max_sim:
        #    max_sim = sim
        #    best_bab = (bab1, bab2)
    
    return sim#, best_bab

#w1[s1, s2, s3]  w2[s1,s2,s3,s4,s5]  w3[s1,s2]
#   s1  s1  s1      [w1s1    w2s1]    [w1s1    w3s1]    [w2s1    w3s1]
#   s1  s1  s2
#   s1  s2  s1
#   s1  s2  s2

#   s1  s1
#   s1  s2
#   s1  s3

def similarity_tuple(tuple_ids, word_to_synset, nasari):       
    sim = 0
    inter = None

    for i, bab_id1 in enumerate(tuple_ids):
        vect = nasari.get(bab_id1)

        if vect is not None:
            bab_set = set(nasari[bab_id1])

            if(inter is None):
                inter = bab_set
            else:
                inter.intersection(bab_set)
        else:
            inter = None    
            break
        #for bab_id2 in tuple_ids[i+1:]:
        #    sim += compute_similarity(bab_id1, bab_id2, nasari)                    
    
    #print(sim)
    if(inter != None):
        sim = len(inter)

    return sim


#concateno in una lista i significati per ogni parola del titolo
def get_babel_ids(title, word_to_synset):
    babel_ids = []
    
    for word in title:
        babel_ids.append(word_to_synset[word])

    return babel_ids

def get_context(title, word_to_synset, nasari):
    context = []

    for chunk in utils.grouper(title, 3):
        print("chunk", chunk)
        babel_ids = get_babel_ids(chunk, word_to_synset)
        
    #wsb.Lesk_algorithm(title[0], title)
    #for babel_id in babel_ids:
    #    print(len(babel_id))
        
        lista_ids = list(itertools.product(*babel_ids))

        print("lunghezza combinazioni", len(lista_ids))
        max_sim_tup = 0
        best_tup_ids = lista_ids[0]

        for tuple_ids in lista_ids:
            #print(tuple_ids)
            sim_tup = similarity_tuple(tuple_ids, word_to_synset, nasari)

            if sim_tup > max_sim_tup:
                max_sim_tup = sim_tup
                best_tup_ids = tuple_ids

        for best_id in best_tup_ids:
            vect = nasari.get(best_id)

            if vect is not None:
                context.append(vect)
    
    print(context)
    return context

    #0  1   2   3
    #01 02  03
    #12 13
    #23
    #print(len(lista_id))
    #for tuple_id in lista_id:
        #print(tuple_id)
    #for word_uno in title:
    #    for word_due in title[1:]:
    #        babel_ids1 = word_to_synset[word_uno]  # estraiamo i significati delle parole
    #        babel_ids2 = word_to_synset[word_due]
    #        sim, best_bab = compute_similarity(babel_ids1, babel_ids2, nasari)

    #return

def clean_text(dictionary):

    unified = utils.unify_name(dictionary["Titolo"])
    dictionary["Titolo"]=utils.delete_stop_words(unified)
    
    for i, paragraph in enumerate(dictionary["Paragrafi"]):
        unified = utils.unify_name(paragraph)
        dictionary["Paragrafi"][i] = utils.delete_stop_words(unified)

    return dictionary

def main():
    #path = "./asset/Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt"
    path = "./asset/People-Arent-Upgrading-Smartphones-as-Quickly-and-That-Is-Bad-for-Apple.txt"
    #path = "./asset/The-Last-Man-on-the-Moon--Eugene-Cernan-gives-a-compelling-account.txt"
    path_synsets = "./asset/synsets.txt"
    path_nasari = "./asset/dd-nasari.txt"

    synsets = utils.read_file_synset(path_synsets)
    word_to_synset = utils.word_to_synset_dict(synsets)

    nasari = utils.read_file_nasari(path_nasari)

    text = utils.read_file(path)
    dictionary = utils.paragraph(text)    
    dictionary = clean_text(dictionary)

    #print(dictionary)
    get_context(dictionary["Titolo"], word_to_synset, nasari)


if __name__ == '__main__':
    main()
