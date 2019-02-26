import requests
from bs4 import BeautifulSoup
from mister_data.search import DataSource


def _parse_sources(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    div_el = soup.find_all("a", {"class": "sent"})
    sauce = []
    for sent in div_el:
        try:
            url = sent["href"]
            sentence = sent.text.replace("\n", " ").split("(via ")[0]
            sentence = " ".join([w.strip() for w in sentence.split(" ") if
                                 w.strip()]).replace(" , ", ", ")
            if sentence and url:
                sauce.append({"url": url, "sentence": sentence})
        except Exception as e:
            pass
    return sauce


class Openie(DataSource):
    def __init__(self):
        DataSource.__init__(self, "http://openie.allenai.org/search")

    def labels(self, query, deep=False):
        """ return parsed result """
        ans = self.keyword_search(query, deep)
        triples = []
        for res in ans:
            triples.append((res["answer"], res["relationship"], query))
            if deep:
                for s in res["sources"]:
                    triples.append((res["answer"], "example_usage", s["sentence"]))
                    triples.append((s["sentence"], "source_url", s["url"]))
        return triples

    def query(self, query):
        """ return raw result (dict) """
        if "?arg1=" not in query:
            return self.keyword_search(query)
        url = self.base_url + query
        return self.parse_search(url)

    def keyword_search(self, query, deep=False):
        arg1 = ""
        rel = ""
        arg2 = query
        corpora = ""
        query = '?arg1=%s&rel=%s&arg2=%s&corpora=%s' % (
            arg1, rel, arg2, corpora)

        url = self.base_url + query
        return self.parse_search(url, deep)

    @staticmethod
    def parse_search(url, deep=False):
        result = []
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        if soup.find("title").text == "Error":
            print("server error, try again later")
            return None
        div_el = soup.find("ul", {"class": "nav nav-tabs"})
        if div_el is None:
            # http://openie.allenai.org/search?arg1=&rel=&arg2=bacteria&corpora=
            for row in soup.find_all("div", {"class": "row"}):
                name = row.find("h3").text
                url = "http://openie.allenai.org" + row.find("a")["href"]
                r = Openie.parse_results(url, deep)
                if r:
                    result += r
        else:
            result = Openie.parse_results(url, deep)

        return result

    @staticmethod
    def parse_results(url, deep=False):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        if soup.find("title").text == "Error":
            return None
        result = []

        div_el = soup.find("ul", {"class": "nav nav-tabs"})
        if div_el is not None:
            # http://openie.allenai.org/search?arg1=what&rel=kills&arg2=bacteria&corpora=
            answers = div_el.find_all("li", {"class": "visible-phone"})
            for a in answers:
                try:
                    ans = a.find("span", {"class": "title-entity"}).text
                    title = a.find("span", {"class": "title-string"}).text
                    url = "http://openie.allenai.org/" + a.find("a")["href"]
                    bucket = {"answer": ans,
                              "relationship": title}
                    if deep:
                          bucket["sources"] = Openie.parse_sources(url)
                    result.append(bucket)
                except Exception as e:
                    pass
        return result

    @staticmethod
    def parse_sources(url):
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')
        div_el = soup.find_all("a", {"class": "sent"})
        sauce = []
        for sent in div_el:
            try:
                url = sent["href"]
                sentence = sent.text.replace("\n", " ").split("(via ")[0]
                sentence = " ".join([w.strip() for w in sentence.split(" ") if
                                     w.strip()]).replace(" , ", ", ")
                if sentence and url:
                    sauce.append({"url": url, "sentence": sentence})
            except Exception as e:
                pass
        return sauce


if __name__ == "__main__":
    from pprint import pprint

    engine = Openie()

    #pprint(engine.labels("bacteria"))
    pprint(engine.query("bacteria"))
