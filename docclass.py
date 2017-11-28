import re
import math
from sqlite3 import dbapi2 as sqlite
import csv


class Classifier(object):
    
    def __init__(self, get_features, dbname, filename=None):
        self.con = sqlite.connect(dbname)
        # Counts of feature/category combinations
        self.fc = dict()
        # Counts of documents in each category
        self.cc = dict()
        self.get_features = get_features

    def loadData(self, ):
        with open('asdf.csv') as algo:
            entrada = csv.reader(algo)
            for reg in entrada:
                string, category =  reg[0].split(';')[1],  reg[0].split(';')[3]
                category = 'positive' if category == '1' else 'negative'
                self.train(string, category)

    def maketables(self):
        self.con.execute('create table words(word, negative, positive)')
        self.con.execute('create table categories(category, count)')
        self.con.commit()

    # Increase the count of a feature/category pair
    def incf(self, f, cat):
        query = self.con.execute("UPDATE words SET %s = %s + 1 WHERE word = '%s'" % (cat, cat, f))
        if query.rowcount == 0:
            self.con.execute("INSERT INTO words(word, negative, positive) VALUES(?,?,?)",
                             (f, 1 if cat == 'negative' else 0, 1 if cat == 'positive' else 0))

        self.con.commit()

    # Increase the count of a category
    def incc(self, cat):
        query = self.con.execute("UPDATE categories SET count = count + 1 WHERE category = '%s'" % cat)
        if query.rowcount == 0:
            self.con.execute("INSERT INTO categories(category, count) VALUES(?,?)",
                             (cat, 1))



    # The number of times a feature has appeared in a category
    def fcount(self, f, cat):
        count = self.con.execute("select %s from words where word='%s'" % (cat, f)).fetchone()[0]
        return count


    # The number of items in a category
    def catcount(self, cat):
        count = self.con.execute("select count from categories where category='%s'" % cat).fetchone()[0]
        return count


     # The total number of items
    def totalcount(self):
        count = 0
        for category in self.categories():
            count += self.con.execute("select sum(%s) from words" % (category)).fetchone()[0]
        return count


     # The list of all categories
    def categories(self):
        categories_list = list(self.con.execute("select category from categories").fetchall())

        return [c[0] for c in categories_list]

    def train(self, item, cat):
        features = self.get_features(item)
        # Increment the count for every feature with this category
        for f in features:
            self.incf(f, cat)
        # Increment the count for this category
        self.incc(cat)

    def fprob(self, f, cat):
        if self.catcount(cat) == 0: 
            return 0
        a = (self.fcount(f, cat) * 1.0)/self.catcount(cat)
        return a

    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        # Calculate current probability
        basicprob = prf(f, cat)
        # Count the number of times this feature has appeared in
        # all categories
        totals = sum([self.fcount(f, c) for c in self.categories()])
        # Calculate the weighted average
        bp = ((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp


class NaiveBayes(Classifier):

    def __init__(self, get_features, dbname):
        Classifier.__init__(self, get_features, dbname)
        self.thresholds = {}

    def docprob(self, item, cat):
        features=self.get_features(item)
        # Multiply the probabilities of all the features together
        p = 1
        for f in features:
            p *= self.weightedprob(f, cat, self.fprob)
        return p

    def prob(self, item, cat):
        catprob = (self.catcount(cat)*1.0)/self.totalcount( )
        docprob = self.docprob(item, cat)
        return docprob*catprob

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        if cat not in self.thresholds:
            return 1.0
        return self.thresholds[cat]

    def classify(self, item, default=None):
        probs = {}
        # Find the category with the highest probability
        max = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max:
                max = probs[cat]
                best = cat
        # Make sure the probability exceeds threshold*next best
        for cat in probs:
            if cat == best:
                continue
            if probs[cat]*self.getthreshold(best) > probs[best]:
                return default
        return best


def sampletrain(cl):
    cl.train('Nobody owns the water.', 'positive')
    cl.train('the quick rabbit jumps fences', 'positive')
    cl.train('buy pharmaceuticals now', 'negative')
    cl.train('make quick money at the online casino', 'negative')
    cl.train('the quick brown fox tumama', 'positive')

def getwords(doc):
    splitter = re.compile('\\W*')
    # Split the words by non-alpha characters
    words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]
    # Return the unique set of words only
    return dict([(w, 1) for w in words])