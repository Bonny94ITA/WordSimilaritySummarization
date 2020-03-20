import metrics
import csv
import pandas as pd
import numpy as np
from nltk.corpus import wordnet as wn

# Lettura file
def read_file():
    array = []
    with open("./asset/sentences.txt") as tsv:
        for line in csv.reader(tsv, delimiter=','):
            array.append(line)
    array.pop(0)
    return array


def main():
    array = read_file()
    print(array)


if __name__ == '__main__':
    main()
