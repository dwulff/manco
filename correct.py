import re
from collections import Counter

class correct:
    '''proposes correction candidates'''


    def __init__(self, lang):
        '''initialize correction'''

        if lang == 'de':
            self.Dict = dict()
            words = open('_cwf/de.txt','rb').read().lower().split('\n')
            for word in words:
                tmp = word.split('\t')
                self.Dict[tmp[0]] = int(tmp[1])
            self.WORDS = Counter(self.Dict)

            #self.WORDS = Counter(re.findall(r'\w+', open('/Users/wulff/Dropbox (2.0)/Work/Software/spellcheck/dictionaries/de.txt').read().lower()))

        if lang == 'en':
            words = re.findall(r'\w+', open('/Users/wulff/nltk_data/corpora/abc/science.txt','rb').read().lower())
            words = [word in words]
            self.WORDS = Counter(words)

        # determine max len
        self.maxlen = 0
        for key in self.WORDS.keys():
            if len(key) > self.maxlen:
                self.maxlen = len(key)

    def words(self, text):
        '''split text into vector of words'''
        return re.findall(r'\w+', text.lower())

    def known(self, words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.WORDS)

    def unknown(self, words):
        "The subset of `words` that do not appear in the dictionary of WORDS."
        seen = set()
        seen_add = seen.add
        WORDS = self.WORDS
        return [x for x in words if not (x in seen or x in WORDS or seen_add(x))]

    def edits1(self, word):
        "All edits that are one edit away from `word`."
        if len(word) <= self.maxlen + 1:
            letters    = 'abcdefghijklmnopqrstuvwxyz'
            splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
            deletes    = [L + R[1:]               for L, R in splits if R]
            transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
            replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
            inserts    = [L + c + R               for L, R in splits for c in letters]
            return set(deletes + transposes + replaces + inserts)
        else:
            return set()

    def edits2(self, word):
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def candidates(self, word):
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

    def P(self, word):
        "Probability of `word`."
        return self.WORDS[word] / sum(self.WORDS.values())

    def correct_max(self, word):
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.P)

    def correct_n(self, word, n):
        # sort by P(word)
        cand = sorted(self.candidates(word), key = self.P)
        return cand[:n]

    def count(self):
        print len(self.WORDS)

    def word(self, word, n = 10):
        if self.known([word]): return []
        return self.correct_n(word.lower(), n)

