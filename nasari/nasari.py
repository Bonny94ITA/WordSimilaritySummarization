import utils
import math
import copy
import itertools
from nltk import word_tokenize
from nltk import sent_tokenize


########## CALCOLO RANKING ##########


# Determinazione del peso di una frase all'interno del paragrafo
def weight_sentence(sent, context, keywords):
    score = 0
    sent_copy = sent.lower()
    for phrase in utils.bonus:
        if phrase in sent_copy:
            score += 1  # Aumento lo score delle frasi dato che contiene delle frasi bonus

    sent_token = utils.unify_name(word_tokenize(sent))
    for word in sent_token:
        if word in context:
            score += 1  # Aumento lo score delle frasi dato che contiene parole del contesto del titolo
        if word in keywords:
            score += 2  # Aumento lo score delle frasi dato che contiene delle keywords
    return score


# Generiamo un elemento della lista rank_paragraph con all'interno il peso del paragrafo e il paragrafo stesso
def weight_paragraph(paragraph, context, keywords):
    sentences = sent_tokenize(paragraph)
    parag = []
    parag_weight = sent_weight = 0

    for i, sent in enumerate(sentences):
        # Determinazione del peso di una frase all'interno del paragrafo
        sent_weight += weight_sentence(sent, context, keywords)
        parag.append([sent_weight, sent, i])
        parag_weight += sent_weight
    parag.sort(reverse=True)  # ordino le frasi all'interno del paragrafo per peso
    return [parag_weight, parag]


# Calcolo della coesione di un paragrafo rispetto agli altri paragrafi, con la word co-occurrence
def coesion_paragraph(parag, paragraphs):
    parag = word_tokenize(copy.deepcopy(parag))
    paragraphs = copy.deepcopy(paragraphs)
    parag = utils.delete_stop_words(parag)
    coesion = 0

    for par in paragraphs:
        par = word_tokenize(par)
        par = utils.delete_stop_words(par)
        if parag != par:
            for w1 in parag:
                if w1 in par:
                    coesion += 1
    print("\n COESIONE ", coesion)

    return coesion * 0.25  # Si può impostare diversi pesi ai valori di coesione


# Determinazione dell'importanza/rank dei paragrafi
def rank_paragraphs(dictionary, context, keywords):
    ranked_parag = []
    for i, parag in enumerate(dictionary["Paragrafi"]):
        # Calcolo della coesione di un paragrafo rispetto agli altri
        coesion = coesion_paragraph(parag, dictionary["Paragrafi"])
        # Peso dei paragrafi, che corrisponde alla somma dei pesi delle frasi
        weighted = weight_paragraph(parag, context, keywords)
        weighted.append(i)
        weighted[0] += coesion  # Aumento lo score del paragrafo in base alla sua coesione
        ranked_parag.append(weighted)

    ranked_parag[0][0] += len(ranked_parag[0][1])  # Aumento lo score del paragrafo dato che è il primo paragrafo
    ranked_parag[-1][0] += len(ranked_parag[-1][1])  # Aumento lo score del paragrafo dato che è l'ultimo paragrafo
    ranked_parag.sort(reverse=True)

    print("\n\n\n RANKING PARAGRAFI")
    for p in ranked_parag:
        print(str(p[2] + 1) + "\t")
    print("\n\n\n")
    return ranked_parag


########## FINE CALCOLO RANKING ##########


# Toglie i duplicati e inserisce in una lista i vettori ottenuti da Nasari
def clean_context(context):
    clean = []
    for c in context:
        if c['vect'] not in clean:
            clean.append(c['vect'])
    return list(itertools.chain(*clean))


########## CALCOLO SIMILARITA' ##########


# Similarità con weighted overlap (formula nelle slide)
def weighted_overlap(vect1, vect2):
    tot = 0.0
    overlap = 0
    for i, elem in enumerate(vect1):
        try:
            index = vect2.index(elem) + 1
            overlap += 1
        except:
            index = -1
        if index != -1:
            tot += (i + 1 + index) ** (-1)
    denominatore = 1.0
    for i in range(1, overlap + 1):
        denominatore += (2 * i) ** (-1)
    return tot / denominatore


# Calcola la similarità tra i due concetti
def compute_similarity(bab_id1, bab_id2, nasari):
    sim = 0
    vect1 = nasari.get(bab_id1)  # Estraiamo il vettore Nasari per ogni babel synset id
    vect2 = nasari.get(bab_id2)
    # print(vect1)
    # print(vect2)
    if vect1 is not None and vect2 is not None:
        sim = weighted_overlap(vect1["vect"], vect2["vect"])
    return math.sqrt(sim)  # return sim


# Calcola l'intersezione tra tutti i vettori per calcolare la similarità
def similarity_tuple_intersection(tuple_ids, nasari):
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


# Somma la similarità di tutte le coppie all'interno della tupla
def similarity_tuple(tuple_ids, nasari):
    sim = 0
    for i, bab_id1 in enumerate(tuple_ids):
        for bab_id2 in tuple_ids[i + 1:]:
            sim += compute_similarity(bab_id1, bab_id2, nasari)
    return sim


########## FINE CALCOLO SIMILARITA' ##########


# Prende il primo vettore di nasari esistente per i babel synset della parola
def get_vector(word, word_to_synset, nasari):
    babel_ids = word_to_synset[word]
    for bab_id in babel_ids:
        vect = nasari.get(bab_id)
        if vect is not None:
            return vect
    return None


# Concateno in una lista i significati ottenuti da BabelNet per ogni parola del titolo
def get_babel_ids(title, word_to_synset):
    babel_ids = []
    for word in title:
        babel_ids.append(word_to_synset[word])
    return babel_ids


# Determinazione del contesto
def get_context(title, word_to_synset, nasari):
    context = []
    # Spezziamo il titolo per evitare di generare troppe combinazioni di sensi
    # Il secondo parametro indica il numero di parole del titolo da tenere in considerazione per determinare il contesto
    # Questo numero si può cambiare
    for chunk in utils.grouper(title, 6):

        print("chunk", chunk)
        babel_ids = get_babel_ids(chunk, word_to_synset)

        # Possibili combinazioni di sensi attraverso il prodotto cartesiano
        lista_ids = list(itertools.product(*babel_ids))
        print("lunghezza combinazioni", len(lista_ids))

        max_sim_tup = 0
        for word in chunk:
            # Inizializziamo la tupla migliore con i primi significati che esistono in Nasari
            best_tup_ids = get_vector(word, word_to_synset, nasari)

        for tuple_ids in lista_ids:  # DUE METODI PER MISURARE LA SIMILARITA'
            # sim_tup = similarity_tuple_intersection(tuple_ids, nasari)
            sim_tup = similarity_tuple(tuple_ids, nasari)
            if sim_tup > max_sim_tup:
                max_sim_tup = sim_tup
                best_tup_ids = tuple_ids

        # Costruisce il contesto del chunk attuale
        for best_id in best_tup_ids:
            vect = nasari.get(best_id)  # Estraiamo da Nasari il vettore dei migliori significati
            if vect is not None:
                context.append(vect)

    return clean_context(context)


# Normalizzazione degli score
def normalize_score(rank_p):
    tot = 0
    for score in rank_p:
        score[0] = score[0] ** -1
        tot += score[0]
    for score in rank_p:
        score[0] = score[0] / tot  # * ratio
    rank_p.sort(reverse=True)  # Ordino per il peso normalizzato


# riassunto complesso
def summarize(rank_p, ratio):
    normalize_score(rank_p)  # Normalizza gli score
    tot_sent = 0

    # Conta il numero di frasi
    for paragraph in rank_p:
        tot_sent += len(paragraph[1])

    num_sent_del = tot_sent_del = round(tot_sent * ratio)  # Numero di frasi da eliminare
    eliminated_sentence = []

    # Elimino frasi finchè ne' ho da eliminare
    while num_sent_del > 0:
        # I paragrafi sono ordinati per peso, il peso più grande indica il paragrafo peggiore.
        # Se i paragrafi con un peso grande non hanno abbastanza frasi al loro interno,
        # quelli restanti, che hanno dei pesi più piccoli,
        # molto probabilmente elimineranno un numero di frasi inferiore al totale da eliminare.
        # Quindi il while ci assicura che vengano eliminate tutte le frasi
        for paragraph in rank_p:
            if len(paragraph[1]) > 0 and num_sent_del > 0:
                num_to_del = paragraph[0] * tot_sent_del
                # Calcolo in base al peso, quante frasi eliminare per il paragrafo corrente per difetto
                if num_to_del < 1:  # elimino almeno una frase
                    sent_del = math.ceil(num_to_del)
                else:
                    sent_del = round(num_to_del)

                # Se il numero di frasi da eliminare e' minore della lunghezza del paragrafo le elimino normalmente
                if sent_del < len(paragraph[1]):
                    eliminated_sentence.append([paragraph[2] + 1, paragraph[1][-sent_del:]])
                    paragraph[1] = paragraph[1][:-sent_del]
                    num_sent_del -= sent_del  # Sottraggo il numero di frasi appena eliminate dal totale
                else:
                    eliminated_sentence.append([paragraph[2] + 1, paragraph[1]])
                    num_sent_del -= len(
                        paragraph[1])  # Il numero di frasi da eliminare supererebbe il numero di frasi nel paragrafo
                    paragraph[1] = []  # Quindi sottraggo solo la lunghezza del paragrafo (svuoto il paragrafo)

    print("\n\n\nELIMINATED SENTENCES " + str(tot_sent_del) + "\n\n\n")
    for sent in eliminated_sentence:
        print(sent)
    return rank_p


# Riassunto semplice
def summarize_trivial(rank_p, ratio):
    tot_sent = 0

    # Contiamo il totale delle frasi
    for paragraph in rank_p:
        tot_sent += len(paragraph[1])

    print("TOTALE DELLE FRASI ", tot_sent)

    # Calcolo numero di frasi da eliminare
    num_sent_del = round(tot_sent * ratio)
    eliminated_sentence = []

    # Finchè ci sono frasi da eliminare
    while num_sent_del > 0:
        for paragraph in reversed(rank_p):  # Partendo dal paragrafo peggiore elimino l'ultima frase del paragrafo
            if len(paragraph[1]) and num_sent_del > 0:
                eliminated_sentence.append([paragraph[2] + 1, paragraph[1][-1:]])
                paragraph[1] = paragraph[1][:-1]
                num_sent_del -= 1

    print("\n\n\nELIMINATED SENTENCES " + str(len(eliminated_sentence)) + "\n\n\n")
    for sent in eliminated_sentence:
        print(sent)
    return rank_p


def main():
    # path = "./asset/Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt"
    path = "./asset/People-Arent-Upgrading-Smartphones-as-Quickly-and-That-Is-Bad-for-Apple.txt"
    # path = "./asset/The-Last-Man-on-the-Moon--Eugene-Cernan-gives-a-compelling-account.txt"
    path_synsets = "./asset/synsets.txt"
    path_nasari = "./asset/dd-nasari.txt"

    # Lettura del file Synset ottenuto con lo script titleSynset.py
    synsets = utils.read_file_synset(path_synsets)
    # Dizionario di synsets con parola come key e babel synset id come valore
    word_to_synset = utils.word_to_synset_dict(synsets)

    # Lettura del file nasari
    nasari = utils.read_file_nasari(path_nasari)

    # Lettura file da testare
    text = utils.read_file(path)

    # Individuazione di 10 keyword nel file
    keywords = utils.get_key_words(text)
    # print(keywords)

    # Divisione del testo in titolo e paragrafi
    dictionary = utils.paragraph(text)
    # Pulizia del titolo con unione dei nomi propri in unico token ed eliminazione delle stop words
    dictionary = utils.clean_title(dictionary)
    # print(dictionary)

    # Determinazione del contesto
    context = get_context(dictionary["Titolo"], word_to_synset, nasari)
    # print(context)
    # context = []

    # Determinazione dell'importanza/rank dei paragrafi
    rank_p = rank_paragraphs(dictionary, context, keywords)
    rank_p2 = copy.deepcopy(rank_p)

    print("\n\n\nORIGINAL\n\n\n" + utils.generate_summary(rank_p))

    # Creazione riassunti con metodo trivial
    summary = summarize_trivial(rank_p2, ratio=0.3)  # Il ratio si può cambiare in base alla percentuale di riassunto
    print("\n\n\nSUMMARY TRIVIAL\n\n\n" + utils.generate_summary(summary))

    # Creazione riassunti con metodo efficiente
    summary = summarize(rank_p, ratio=0.3)  # Il ratio si può cambiare in base alla percentuale di riassunto
    print("\n\n\nSUMMARY\n\n\n" + utils.generate_summary(summary))

    # Salvataggio riassunti
    utils.save_summary(summary)


if __name__ == '__main__':
    main()
