import utils
from nltk import word_tokenize
from nltk.corpus import wordnet as wn


def main():
    array = utils.read_file()
    print(array)
    array = utils.extract_word(array)
    print(array)
    print(len(array))


if __name__ == '__main__':
    main()
