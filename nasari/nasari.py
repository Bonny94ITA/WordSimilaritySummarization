import utils
import csv
import pandas as pd
import numpy as np
from nltk.corpus import wordnet as wn


def main():
    path = "./asset/Donald-Trump-vs-Barack-Obama-on-Nuclear-Weapons-in-East-Asia.txt"
    # path = "./asset/People-Arent-Upgrading-Smartphones-as-Quickly-and-That-Is-Bad-for-Apple.txt"
    # path = "./asset/The-Last-Man-on-the-Moon--Eugene-Cernan-gives-a-compelling-account.txt"
    text = utils.read_file(path)
    dictionary = utils.paragraph(text)
    tmp = utils.delete_stop_words(dictionary["Titolo"])
    print(tmp)
    #print(dictionary)


if __name__ == '__main__':
    main()
