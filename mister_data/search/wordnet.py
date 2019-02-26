from nltk.corpus import wordnet as wn

try:

    def wordnet_test():
        synsets = wn.synsets("natural language processing")

except LookupError:
    import nltk

    def download_wordnet():
        print("downloading wordnet")
        nltk.download("wordnet")

    download_wordnet()

from mister_data.search import DataSource


class Wordnet(DataSource):
    def __init__(self):
        DataSource.__init__(self, "http://www.nltk.org/howto/wordnet.html")

    @staticmethod
    def get_synsets(word, pos=wn.NOUN):
        synsets = wn.synsets(word, pos=pos)
        if not len(synsets):
            return []
        return synsets

    @staticmethod
    def get_definition(word, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(word, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        return synset.definition()

    @staticmethod
    def get_examples(word, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(word, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        return synset.examples()

    @staticmethod
    def get_lemmas(word, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(word, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        return [l.name().replace("_", " ") for l in synset.lemmas()]

    @staticmethod
    def get_hypernyms(word, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(word, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        return [l.name().split(".")[0].replace("_", " ") for l in
                synset.hypernyms()]

    @staticmethod
    def get_hyponyms(word, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(word, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        return [l.name().split(".")[0].replace("_", " ") for l in
                synset.hyponyms()]

    @staticmethod
    def get_holonyms(word, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(word, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        return [l.name().split(".")[0].replace("_", " ") for l in
                synset.member_holonyms()]

    @staticmethod
    def get_root_hypernyms(word, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(word, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        return [l.name().split(".")[0].replace("_", " ") for l in
                synset.root_hypernyms()]

    @staticmethod
    def common_hypernyms(word, word2, pos=wn.NOUN):
        synsets = wn.synsets(word, pos=pos)
        if not len(synsets):
            return []
        synset = synsets[0]
        synsets = wn.synsets(word2, pos=pos)
        if not len(synsets):
            return []
        synset2 = synsets[0]
        return [l.name().split(".")[0].replace("_", " ") for l in
                synset.lowest_common_hypernyms(synset2)]

    @staticmethod
    def get_antonyms(word, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(word, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        lemmas = synset.lemmas()
        if not len(lemmas):
            return []
        lemma = lemmas[0]
        antonyms = lemma.antonyms()
        return [l.name().split(".")[0].replace("_", " ") for l in antonyms]

    def labels(self, query, pos=wn.NOUN, synset=None):
        """ return parsed result """
        triples = []
        triples.append((query, "definition",
                        self.get_definition(query, pos=pos, synset=synset)))
        for l in self.get_synsets(query, pos=pos):  # antonyms
            triples.append((query, "synset", l.name()))
        for l in self.get_lemmas(query, pos=pos, synset=synset):  # synonyms/rewordings of dog
            triples.append((query, "lemma", l))
            triples.append((query, "same as", l))
            triples.append((query, "synonym", l))
        for l in self.get_antonyms(query, pos=pos, synset=synset):  # antonyms
            triples.append((query, "antonym", l))
        for l in self.get_holonyms(query, pos=pos, synset=synset):  # dog is part of
            triples.append((query, "holonym", l))
            triples.append((query, "part of", l))
        for l in self.get_hyponyms(query, pos=pos, synset=synset):  # are instances of dog
            triples.append((query, "hyponym", l))
            triples.append((query, "instance of", l))
        for l in self.get_hypernyms(query, pos=pos, synset=synset):  # dog is instance of
            triples.append((query, "instance of", l))
            triples.append((query, "hypernym", l))
            triples.append((query, "label", l))
        for l in self.get_root_hypernyms(query, pos=pos, synset=synset):  # highest instance for dog
            triples.append((query, "instance of", l))
            triples.append((query, "root_hypernym", l))
            triples.append((query, "hypernym", l))
        # for l in common_hypernyms(word): # common instances for dog and chicken
        return triples

    def query(self, query, pos=wn.NOUN, synset=None):
        if synset is None:
            synsets = wn.synsets(query, pos=pos)
            if not len(synsets):
                return ""
            synset = synsets[0]
        res = {"lemmas": self.get_lemmas(query, pos=pos, synset=synset),
               "antonyms": self.get_antonyms(query, pos=pos, synset=synset),
               "holonyms": self.get_holonyms(query, pos=pos, synset=synset),
               "hyponyms": self.get_hyponyms(query, pos=pos, synset=synset),
               "hypernyms": self.get_hypernyms(query, pos=pos, synset=synset),
               "root_hypernyms": self.get_root_hypernyms(query, pos=pos, synset=synset),
               "definition": self.get_definition(query, pos=pos, synset=synset)}
        return res


if __name__ == "__main__":
    from pprint import pprint

    engine = Wordnet()
    subject = "dog"
    pprint(engine.query(subject))
    pprint(engine.labels(subject))


