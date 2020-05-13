import utils


# Estrazione dei synset e scrittura su file
def write_synset(title, tsv):
    for lemma in title:
        tsv.write("#" + lemma + "\n")
        for synset in utils.get_synset(lemma):  # Estrazione da Babelnet dei synset
            tsv.write(synset["id"] + "\n")


# Per ogni parola rilevante dei titoli dei file recuperiamo i babelsynset id da BabelNet
# e li salviamo su file per evitare di fare la richiesta a ogni esecuzione del riassunto automatico
def main():
    paths = ["./asset/Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt",
             "./asset/People-Arent-Upgrading-Smartphones-as-Quickly-and-That-Is-Bad-for-Apple.txt",
             "./asset/The-Last-Man-on-the-Moon--Eugene-Cernan-gives-a-compelling-account.txt"]
    with open("./asset/synsets.txt", "w") as tsv:
        for path in paths:
            text = utils.read_file(path)  # Lettura dei file
            dictionary = utils.paragraph(text)  # Divisione del testo in titolo e paragrafi
            unified = utils.unify_name(dictionary["Titolo"])  # Unione dei nomi propri nel titolo
            title = utils.delete_stop_words(unified)  # Eliminazione delle stop words
            write_synset(title, tsv)  # Estrazione dei synset e scrittura su file


if __name__ == '__main__':
    main()
