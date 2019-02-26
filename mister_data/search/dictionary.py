from vocabulary.vocabulary import Vocabulary as vb
from mister_data.search import DataSource


class Dictionary(DataSource):
    def __init__(self):
        DataSource.__init__(self, "https://github.com/tasdikrahman/vocabulary")

    def labels(self, query):
        """ return parsed result """
        res = []
        meanings = vb.meaning(query, format="list")
        if meanings:
            meanings = [e.replace("<i>", "").replace("</i>", "")
                        .replace("[i]", "").replace("[/i]", "")
                        for e in meanings]
            for e in meanings:
                res.append((query, "meaning", e))
        synonyms = vb.synonym(query, format="list")
        if synonyms:
            for e in synonyms:
                res.append((query, "synonym", e))
        antonyms = vb.antonym(query, format="list")
        if antonyms:
            for e in antonyms:
                res.append((query, "antonym", e))

        #ps = vb.part_of_speech(query, format="list")
        #if ps:
        #    for e in ps:
        #        res.append((query, "part_of_speech", e))
        examples = vb.usage_example(query, format="list")
        if examples:
            for e in examples:
                res.append((query, "usage_example", e))
        return res

    def query(self, query):
        """ return raw result (dict) """
        cons = {"meaning": [], "synonym": [], "antonym": [],
                "usage_example": [], "part of speech": []}
        meanings = vb.meaning(query, format="list")
        if meanings:
            cons["meaning"] = [
                e.replace("<i>", "").replace("</i>", "")
                    .replace("[i]", "").replace("[/i]", "") for e in meanings]
        synonyms = vb.synonym(query, format="list")
        if synonyms:
            cons["synonym"] = synonyms
        antonyms = vb.antonym(query, format="list")
        if antonyms:
            cons["antonym"] = antonyms
        ps = vb.part_of_speech(query, format="list")
        if ps:
            cons["part of speech"] = ps
        examples = vb.usage_example(query, format="list")
        if examples:
            cons["usage_example"] = [e.replace("[", "").replace("]", "") for
                                    e in examples]
        return cons


if __name__ == "__main__":
    from pprint import pprint

    engine = Dictionary()
    subject = "dog"
    pprint(engine.query(subject))
    pprint(engine.labels(subject))
