import csv
from nltk.corpus import wordnet as wn


class WuPalmer:

    def __init__(self):
        list = self.read_file()
        for item in list:
            x, y = self.get_synsets(item)
            max_similarity = 0.0

            # Confronto ogni senso i del primo termine con tutti i sensi j del secondo termine
            for i in x:
                for j in y:

                    similarity = self.wup_similarity(i, j)

                    if similarity is not None:
                        if max_similarity < similarity:
                            max_similarity = similarity

                    # Wu-Palmer Similarity di NTLK
                    # if i.wup_similarity(j) is not None:
                    #     if max_similarity < i.wup_similarity(j):
                    #         max_similarity = i.wup_similarity(j)

            print(item, max_similarity)

    @staticmethod
    def read_file():
        list = []
        with open("./asset/WordSim353.csv") as tsv:
            for line in csv.reader(tsv, delimiter=','):
                list.append(line)
        list.pop(0)
        return list

    @staticmethod
    def get_synsets(item):
        return wn.synsets(item[0]), wn.synsets(item[1])

    @staticmethod
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


if __name__ == '__main__':
    WuPalmer()
