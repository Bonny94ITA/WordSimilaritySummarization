import utils
import math
import itertools
import importlib.util
from nltk import word_tokenize
from nltk import sent_tokenize

spec = importlib.util.spec_from_file_location("wordSenseDisambiguation",
                                              "../wordSenseDisambiguation/wordSenseDisambiguation.py")
wsb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wsb)


# similarità con weighted overlap
def weighted_overlap(vect1, vect2):
    tot = 0.0
    overlap = 0
    for i, elem in enumerate(vect1):
        try:
            index = vect2.index(elem) + 1
            overlap += 1
        except:
            index = -1

        if (index != -1):
            tot += (i + 1 + index) ** (-1)

    denominatore = 1.0

    for i in range(1, overlap + 1):
        denominatore += (2 * i) ** (-1)

    return tot / denominatore


# calcola la similarità tra i due concetti
def compute_similarity(bab_id1, bab_id2, nasari):
    sim = 0

    vect1 = nasari.get(bab_id1)  # Estraiamo il vettore per ogni babel synset id
    vect2 = nasari.get(bab_id2)

    # print(vect1)
    # print(vect2)

    if vect1 is not None and vect2 is not None:
        sim = weighted_overlap(vect1["vect"], vect2["vect"])

    return sim


# somma la similarità della tupla
def similarity_tuple(tuple_ids, word_to_synset, nasari):
    sim = 0

    for i, bab_id1 in enumerate(tuple_ids):
        for bab_id2 in tuple_ids[i + 1:]:
            sim += compute_similarity(bab_id1, bab_id2, nasari)

            # print(sim)

    return sim


# fa l'intersezione tra tutti i vettori per calcolare la similarità
def similarity_tuple_intersection(tuple_ids, word_to_synset, nasari):
    sim = 0
    inter = None

    for i, bab_id1 in enumerate(tuple_ids):
        vect = nasari.get(bab_id1)

        if vect is not None:
            bab_set = set(nasari[bab_id1])

            if inter is None:
                inter = bab_set
            else:
                inter.intersection(bab_set)
        else:
            inter = None
            break

            # print(sim)
    if inter != None:
        sim = len(inter)

    return sim


# concateno in una lista i significati per ogni parola del titolo
def get_babel_ids(title, word_to_synset):
    babel_ids = []

    for word in title:
        babel_ids.append(word_to_synset[word])

    return babel_ids


# prende il primo vettore di nasari esistente per i babel synset della parola
def get_vector(word, word_to_synset, nasari):
    babel_ids = word_to_synset[word]

    for bab_id in babel_ids:
        vect = nasari.get(bab_id)

        if vect is not None:
            return vect
    return None


def clean_context(context):
    clean_context = []

    for c in context:
        if c['vect'] not in clean_context:
            clean_context.append(c['vect'])
    return list(itertools.chain(*clean_context))


def get_context(title, word_to_synset, nasari):
    context = []

    for chunk in utils.grouper(title, 6):  # il numero cambia la dimensione del contesto da tenere in considerazione

        print("chunk", chunk)
        babel_ids = get_babel_ids(chunk, word_to_synset)

        lista_ids = list(itertools.product(*babel_ids))

        print("lunghezza combinazioni", len(lista_ids))
        max_sim_tup = 0
        best_tup_ids = lista_ids[0]

        for tuple_ids in lista_ids:  # Ci sono due metodi per misurare la similarità
            # sim_tup = similarity_tuple_intersection(tuple_ids, word_to_synset, nasari)
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


def clean_title(dictionary):
    unified = utils.unify_name(dictionary["Titolo"])
    dictionary["Titolo"] = utils.delete_stop_words(unified)
    return dictionary


def weight_sentence(sent, context, keywords):
    score = 0

    sent_copy = sent.lower()
    for phrase in utils.bonus:
        if phrase in sent_copy:
            score += 1  # aumento score dato che contiene delle frasi bonus

    sent_token = utils.unify_name(word_tokenize(sent))
    for word in sent_token:
        if word in context:
            score += 1  # aumento score dato che contiene parole del contesto del titolo
        if word in keywords:
            score += 2  # aumento score dato che contiene delle keywords
    return score


def weight_paragraph(paragraph, context, keywords):
    sentences = sent_tokenize(paragraph)
    parag = []
    parag_weight = 0
    sent_weight = 0

    for i, sent in enumerate(sentences):
        sent_weight += weight_sentence(sent, context, keywords)
        parag.append([sent_weight, sent, i])
        parag_weight += sent_weight
    parag.sort(reverse=True)
    return [parag_weight, parag]


def rank_paragraphs(dictionary, context, keywords):
    ranked_parag = []

    for i, paragh in enumerate(dictionary["Paragrafi"]):
        weighted = weight_paragraph(paragh, context, keywords)
        weighted.append(i)
        ranked_parag.append(weighted)
    ranked_parag[0][0] += 2  # aumento score dato che è il primo paragrafo
    ranked_parag[-1][0] += 2  # aumento score dato che è l'ultimo paragrafo
    #ranked_parag.sort(reverse=True)
    #print(ranked_parag)
    return ranked_parag

#normalizzo gli score
def normalize_score(rank_p):
    tot = 0
    for score in rank_p:
        score[0] = score[0] ** -1
        tot += score[0]
    ok = 0
    for score in rank_p:
        score[0] = score[0] / tot #* ratio
        ok+= score[0]
    
    rank_p.sort(reverse=True)#ordino per il peso normalizzato
    print("TOT SCORE", ok)


def summarize(rank_p, ratio):
    normalize_score(rank_p)
    
    tot_sent = 0
    
    for paragraph in rank_p:
        tot_sent+=len(paragraph[1])

    num_sent_del=tot_sent_del=math.ceil(tot_sent*ratio) #numero di frasi da eliminare    

    #print(num_sent_del)

    #elimino frasi finchè ne' ho da eliminare
    while(num_sent_del > 0):    # il while c'è perchè il for potrebbe terminare senza eliminare tutte le frasi,
        print(num_sent_del)     # perchè se alcuni paragrafi con un peso grande non avevano abbastanza frasi, 
                                # quelli restanti hanno dei pesi più piccoli e la loro quota di frasi potrebbe
                                # non raggiungere il totale di frasi da eliminare
        for paragraph in rank_p:
            if(num_sent_del > 0):
                num_to_del = paragraph[0] * tot_sent_del

                #calcolo in base al peso, quante frasi eliminare per il paragrafo corrente per difetto
                if(num_to_del < 1): #elimino almeno una frase
                    sent_del=math.ceil(num_to_del)
                else:
                    sent_del=math.floor(num_to_del)                
                
                #se il numero di frasi da eliminare e' minore della lunghezza del paragrafo le elimino normalmente
                if(sent_del < len(paragraph[1])):
                    paragraph[1] = paragraph[1][:-sent_del]
                    num_sent_del-=sent_del  #sottraggo il numero di frasi appena eliminate
                else:
                    num_sent_del-=len(paragraph[1]) #il numero di frasi da eliminare supererebbe il numero di frasi nel paragrafo
                    paragraph[1] = []               #quindi sottraggo solo la lunghezza del paragrafo
            else:
                break
        
        tot_sent_del = num_sent_del #i pesi vanno ricalibrati sulle frasi restanti da eliminare nel caso ce ne siano ancora
    print(rank_p)

    return rank_p

def summarize_trivial(rank_p, ratio):

    tot_sent = 0
    
    for paragraph in rank_p:
        tot_sent+=len(paragraph[1])

    num_sent_del=math.ceil(tot_sent*ratio)

    print(num_sent_del)

    #print(rank_p[-5:-4])
    while(num_sent_del>0):
        for paragraph in reversed(rank_p):
            if(len(paragraph[1]) and num_sent_del > 0):
                paragraph[1]=paragraph[1][:-1]
                num_sent_del-=1

    #print(rank_p[-5:-4])

    return rank_p

def saveSummary(summary):
    summary.sort(key=lambda x: x[2])

    with open("./asset/summary_90.txt", "w", encoding='utf8') as output:
    #with open("./asset/summary_trivial.txt", "w", encoding='utf8') as output:
        text_summary = ""
        for paragraph in summary:
            paragraph[1].sort(key=lambda x: x[2])
            
            for sentence in paragraph[1]:
                text_summary+=sentence[1]+" "

            text_summary+="\n\n"

        output.write(text_summary)
        #print(text_summary)

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
    # print(keywords)

    dictionary = utils.paragraph(text)
    dictionary = clean_title(dictionary)
    # print(dictionary)

    context = get_context(dictionary["Titolo"], word_to_synset, nasari)
    # print(context)
    #context = []

    rank_p = rank_paragraphs(dictionary, context, keywords)
    summary = summarize(rank_p, ratio=0.9)
    #summary = summarize_trivial(rank_p, ratio=0.3)
    saveSummary(summary)


if __name__ == '__main__':
    main()
