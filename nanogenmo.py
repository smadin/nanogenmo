# NaNoGenMo Project
# Generate a NaNoWriMo-qualifying "novel" -- i.e. a body of text containing at least 50,000 words.
# This is version 1.0
# TODO:
# * present user with menu of randomly-chosen seed pages for related mode (e.g. "write novel about A) ____ B) _____ or C) _____ ?")
# * sources other than Wikipedia
# * user-configurable sources?
# * regenerate Markov database from a new wikipedia page (or page and related pages?) for each chapter?

import sys
from random import Random
from pymarkovchain import MarkovChain
import wikipedia
import argparse

def setup_argparse():
    parser = argparse.ArgumentParser(description='Generates NaNoWriMo-qualifying "novels" from Markov chains based on Wikipedia articles. Builds the Markov database either from random Wikipedia pages, or by following related links from the first page.')
    parser.add_argument('-wl', '--wordlen', dest='word_len', default=5.1, type=float, help='average word length (default 5.1 letters)')
    parser.add_argument('-ds', '--dataset', dest='dataset_size', default=10000, type=int, help='target number of words for source data set (default 10,000)')
    parser.add_argument('-wc', '--wordcount', dest='word_count', default=50000, type=int, help='target word count for output (default 50,000)')
    parser.add_argument('-c', '--chapters', dest='chapters', default=12, type=int, help='number of chapters in output (default 12)')
    parser.add_argument('-gn', '--graf-min', dest='graf_min', default=1, type=int, help='minimum sentences per paragraph (default 1)')
    parser.add_argument('-gx', '--graf-max', dest='graf_max', default=10, type=int, help='maximum sentences per paragraph (default 10)')
    parser.add_argument('-s', '--search-term', dest='search_term', default=None, type=str, help='Wikipedia search term to base source database on (default: use a random page)')
    parser.add_argument('-r', '--related', action='store_const', const=True, default=False, dest="related", help='Use "related" section links instead of random pages to build database (default: use all random pages)')

    return parser

# this function barely saves any code, but I think it improves readability
def wordcount(string):
    return len(string.split(" "))

class NaNoGenMo:
    def __init__(self, avg_wordlen, min_dataset_size, target_wordcount, num_chaps, min_graf_len, max_graf_len, search_term, related):
        self.WORDLEN = avg_wordlen
        self.DATASET = min_dataset_size
        self.WORDCNT = target_wordcount
        self.NUM_CHAPS = num_chaps
        self.GRAF_MIN = min_graf_len
        self.GRAF_MAX = max_graf_len
        self.SEARCH_TERM = search_term
        self.RELATED = related
        self.rand = Random()

    def set_dict(self, dictfile):
        self.dictfile = dictfile

    def build_source(self):
        source = ""
        # grab random Wikipedia pages until we have enough bytes to (probably) have at least DATASET words.
        iterations = 0
        page = None
        while len(source) < self.WORDLEN * self.DATASET:
            title = wikipedia.random()
            if self.RELATED == True:
                sys.stderr.write("using related mode\n")
                if iterations == 0:
                    sys.stderr.write("first page\n")
                    if self.SEARCH_TERM is not None:
                        sys.stderr.write("using search term \"%s\" instead of random\n" % self.SEARCH_TERM)
                        title = self.SEARCH_TERM
                    else:
                        sys.stderr.write("using random page title \"%s\"\n" % title)
                else:
                    if len(page.links) > 0:
                        ix = self.rand.randint(0, len(page.links) - 1)
                        title = page.links[ix]
                        sys.stderr.write("using related page title \"%s\"\n" % title)
            else:
                sys.stderr.write("using all random page titles. this one is \"%s\"\n" % title)
            iterations += 1

            # this is in a try/except because wikipedia.page() will throw an exception if it only gets a
            # disambiguation page. we don't care about that, so we just try another random title.
            try:
                page = wikipedia.page(title)
                # remove Wikipedia's section markers. there's probably an easier way to do that. If we leave them in
                # pymarkovchain treats them as "words", so the output text is full of "===" and whatnot.
                content = page.content.replace("====", "").replace("===", "").replace("==", "")
                source += "\n" + content
                # TODO: instead of completely random pages, this could start with a random wiki page, then expand its
                # dataset by following links from that page. that might produce somewhat more apparent thematic coherence
                # but on the other hand it might not.
            except:
                pass
        return source

    def prepare_dict(self):
        if self.dictfile is None:
            print "error: no dictfile"
            return
        # now build the markov database. just using pymarkovchain's default settings for now. will fail if it doesn't
        # have write access to $PWD.
        chain = MarkovChain("./markov")

        source = self.build_source()
        chain.generateDatabase(source)

        # seem to need to do this to reload the database after generating it
        self.chain = MarkovChain("./markov")

    def generate(self):
        novel = ""
        chap = ""
        chapnum = 1

        # now generate the actual novel, sentence by sentence, until it's at least WORDCNT words.
        while wordcount(novel) < self.WORDCNT:
            # chapter headings and paragraph breaks make it more readable.
            chap = "\n\n===CHAPTER %d===\n\n" % chapnum
            # for now we're just making roughly equal-sized chapters.
            while wordcount(chap) < (self.WORDCNT / self.NUM_CHAPS):
                graf = ""
                s = 0
                # how many sentences for this paragraph?
                gl = self.rand.randint(self.GRAF_MIN, self.GRAF_MAX)
                while s < gl:
                    # if this isn't the first sentence in the paragraph, append a space after the last one.
                    if len(graf) > 0:
                        graf += " "
                    # if this isn't the first paragraph in the chapter, start it with a tab.
                    elif len(chap) > 0:
                        graf += "\t"
                    # generate the actual string
                    graf += self.chain.generateString()
                    # simplistic weighted random selection of sentence-ending punctuation. 70% chance of a period,
                    # 20% chance of a question mark, 10% chance of an exclamation point. those are guessed values, I
                    # haven't made any effort to assess whether it feels "right" in the resulting text.
                    i = self.rand.randint(0, 10)
                    if i <= 7:
                        graf += "."
                    elif i <= 9:
                        graf += "?"
                    else:
                        graf += "!"
                    s += 1
                # blank lines between paragraphs
                chap += graf
                chap += "\n\n"
            chapnum += 1
            novel += chap
        return novel

def run(args):
    nanogenmo = NaNoGenMo(args.word_len, args.dataset_size, args.word_count, args.chapters, args.graf_min, args.graf_max, args.search_term, args.related)
    nanogenmo.set_dict("./markov")
    nanogenmo.prepare_dict()
    novel = nanogenmo.generate()

    # Wikipedia text will have Unicode characters in it; we'll get an exception trying to print this if we don't
    # use encode().
    print novel.encode('utf-8')
    pass

if __name__ == "__main__":
    parser = setup_argparse()
    args = parser.parse_args()

    run(args)
