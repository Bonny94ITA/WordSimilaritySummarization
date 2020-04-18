import utils
import itertools
import importlib.util
from nltk import word_tokenize
import random
from nltk import sent_tokenize

spec = importlib.util.spec_from_file_location("wordSenseDisambiguation", "../wordSenseDisambiguation/wordSenseDisambiguation.py")
wsb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wsb)

#similarità con weighted overlap
def weighted_overlap(vect1, vect2):

    tot = 0.0
    overlap = 0
    for i, elem in enumerate(vect1):
        try:
            index = vect2.index(elem)+1
            overlap += 1
        except:
            index = -1
        
        if(index != -1):
            tot+= (i+1+index)**(-1)

    denominatore = 1.0

    for i in range (1, overlap+1):
        denominatore += (2*i)**(-1)

    return tot/denominatore

# calcola la similarità tra i due concetti
def compute_similarity(bab_id1, bab_id2, nasari):
    sim = 0

    vect1 = nasari.get(bab_id1)  # Estraiamo il vettore per ogni babel synset id
    vect2 = nasari.get(bab_id2)

    #print(vect1)
    #print(vect2)

    if vect1 is not None and vect2 is not None:
        sim = weighted_overlap(vect1["vect"], vect2["vect"])
    
    return sim

#somma la similarità della tupla
def similarity_tuple(tuple_ids, word_to_synset, nasari):       
    sim = 0

    for i, bab_id1 in enumerate(tuple_ids):        
        for bab_id2 in tuple_ids[i+1:]:
            sim += compute_similarity(bab_id1, bab_id2, nasari)                    
    
    #print(sim)

    return sim

#fa l'intersezione tra tutti i vettori per calcolare la similarità
def similarity_tuple_intersection(tuple_ids, word_to_synset, nasari):       
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

#prende il primo vettore di nasari esistente per i babel synset della parola
def get_vector(word, word_to_synset, nasari):
    babel_ids = word_to_synset[word]

    for bab_id in babel_ids:
        vect = nasari.get(bab_id)
        
        if(vect is not None):
            return vect

    return None

def clean_context(context):
    
    clean_context = []

    for c in context:        
        if c not in clean_context:            
            clean_context.append(c)
    
    return clean_context


def get_context(title, word_to_synset, nasari):
    context = []

    for chunk in utils.grouper(title, 6):#il numero cambia la dimensione del contesto da tenere in considerazione

        print("chunk", chunk)
        babel_ids = get_babel_ids(chunk, word_to_synset)
        
        lista_ids = list(itertools.product(*babel_ids))

        print("lunghezza combinazioni", len(lista_ids))
        max_sim_tup = 0
        best_tup_ids = lista_ids[0]

        for tuple_ids in lista_ids:# Ci sono due metodi per misurare la similarità            
            #sim_tup = similarity_tuple_intersection(tuple_ids, word_to_synset, nasari)
            sim_tup = similarity_tuple(tuple_ids, word_to_synset, nasari)

            if sim_tup > max_sim_tup:
                max_sim_tup = sim_tup
                best_tup_ids = tuple_ids

        for j, best_id in enumerate(best_tup_ids):
            vect = nasari.get(best_id)

            if vect is not None:
                context.append(vect)
            else:
                vect = get_vector(chunk[j], word_to_synset, nasari)

                if vect is not None:
                    context.append(vect)
                
    context = clean_context(context)    
    return context

def clean_text(dictionary):

    unified = utils.unify_name(dictionary["Titolo"])
    dictionary["Titolo"]=utils.delete_stop_words(unified)
    
    for i, paragraph in enumerate(dictionary["Paragrafi"]):
        unified = utils.unify_name(paragraph)
        dictionary["Paragrafi"][i] = utils.delete_stop_words(unified)

    return dictionary

def weight_sentence(sent, context):
    return

def weight_paragraph(paragraph, context):
    sentences = sent_tokenize(paragraph)

    parag_weight = 0.0
    parag = []

    for sent in sentences:
        sent_weight+=weight_sentence(sent, context)
        parag.append([sent, parag_weight])
        parag_weight+=sent_weight

    return [parag_weight, parag]
    

def rank_paragraphs(dictionary, context):

    ranked_parag = []

    for paragh in dictionary["Paragrafi"]:
        ranked_parag.append(weight_paragraph(paragh, context))

    return ranked_parag


def main():
    #path = "./asset/Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt"
    #path = "./asset/People-Arent-Upgrading-Smartphones-as-Quickly-and-That-Is-Bad-for-Apple.txt"
    path = "./asset/The-Last-Man-on-the-Moon--Eugene-Cernan-gives-a-compelling-account.txt"
    path_synsets = "./asset/synsets.txt"
    path_nasari = "./asset/dd-nasari.txt"

    synsets = utils.read_file_synset(path_synsets)
    word_to_synset = utils.word_to_synset_dict(synsets)

    nasari = utils.read_file_nasari(path_nasari)

    text = utils.read_file(path)

    keywords = utils.get_key_words(text)

    print(keywords)

    dictionary = utils.paragraph(text)    
    dictionary = clean_text(dictionary)

    #print(dictionary)
    #context = get_context(dictionary["Titolo"], word_to_synset, nasari)


    #rank_paragraphs(dictionary, context)

    print(context)


if __name__ == '__main__':
    main()
