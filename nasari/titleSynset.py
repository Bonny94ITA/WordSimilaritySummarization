import utils


def get_synset(title, tsv):
    for lemma in title:
        tsv.write("#" + lemma + "\n")
        for synset in utils.get_synset(lemma):
            tsv.write(synset["id"] + "\n")


def main():
    paths = ["./asset/Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt",
             "./asset/People-Arent-Upgrading-Smartphones-as-Quickly-and-That-Is-Bad-for-Apple.txt",
             "./asset/The-Last-Man-on-the-Moon--Eugene-Cernan-gives-a-compelling-account.txt"]
    with open("./asset/synsets.txt", "w") as tsv:
        for path in paths:
            text = utils.read_file(path)
            dictionary = utils.paragraph(text)
            title = utils.delete_stop_words(dictionary["Titolo"])
            get_synset(title, tsv)


if __name__ == '__main__':
    main()
