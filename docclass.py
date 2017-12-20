import re
from sqlite3 import dbapi2 as sqlite
import csv


class Classifier(object):
    """
    Contiene las funciones relacionadas con extraer y guardar datos
    """

    MAX_CONNECTION_RANGE = 4  # Miramos hasta que rango de connexion tenemos en cuenta
    CONNECTION_INIT_COUNTER = 100  # El valor con el que se inician la entrada en base de datos de las connexiones
    # Lista de palabras(preposiciones y articulos) que no tenemos en cuenta
    NEGLIGIBLE_WORDS = ['few'
                        'everi'
                        'most'
                        'thatlittl'
                        'half'
                        'much'
                        'the'
                        'other'
                        'her'
                        'my'
                        'their'
                        'a'
                        'an'
                        'hi'
                        'neither'
                        'these'
                        'all'
                        'it'
                        'no'
                        'thi'
                        'ani'
                        'those'
                        'both'
                        'least'
                        'our'
                        'what'
                        'each'
                        'less'
                        'sever'
                        'which'
                        'either'
                        'mani'
                        'some'
                        'whose'
                        'enough'
                        'more'
                        'such'
                        'your'
                        'aboard'
                        'about'
                        'abov'
                        'across'
                        'after'
                        'against'
                        'along'
                        'amid'
                        'among'
                        'anti'
                        'around'
                        'as'
                        'at'
                        'befor'
                        'behind'
                        'below'
                        'beneath'
                        'besid'
                        'besid'
                        'between'
                        'beyond'
                        'but'
                        'by'
                        'concern'
                        'consid'
                        'despit'
                        'down'
                        'dure'
                        'except'
                        'except'
                        'exclud'
                        'follow'
                        'for'
                        'from'
                        'in'
                        'insid'
                        'into'
                        'like'
                        'minu'
                        'near'
                        'of'
                        'off'
                        'on'
                        'onto'
                        'opposit'
                        'outsid'
                        'over'
                        'past'
                        'per'
                        'plu'
                        'regard'
                        'round'
                        'save'
                        'sinc'
                        'than'
                        'through'
                        'to'
                        'toward'
                        'toward'
                        'under'
                        'underneath'
                        'unlik'
                        'until'
                        'up'
                        'upon'
                        'versu'
                        'via'
                        'with'
                        'within'
                        'without'
                        ]
    
    def __init__(self, db_name):
        """
        Init de la clase, crea la conexion con la base de datos
        :param db_name: (string) Nombre de las base de datos
        """
        self.con = sqlite.connect(db_name)

    def load_data(self, csv_name, maximum=None, start_line=None):
        """
        Carga los datos de un csv y los guarda en base de datos
        :param csv_name: (string) El nombre del csv
        :param maximum: (int) El maximo de lineas en default se guardaran todas
        :param start_line: (int) La linia inicial, el default es 0
        """
        counter = 0
        with open(csv_name) as db:
            data = csv.reader(db)
            for line in data:
                if start_line:
                    if line[0].split(';')[0] < start_line:
                        continue
                string, category = line[0].split(';')[1],  line[0].split(';')[3]
                category = 'positive' if category == '1' else 'negative'
                self.train(string, category)
                if maximum:
                    counter += 1
                    print('%d/%d' % (counter, maximum))
                    if counter > maximum:
                        break

    def make_tables(self):
        """
        Crea las tablas necesarias para guardar los datos
        """
        self.con.execute('create table words(word, negative, positive)')
        self.con.execute('create table categories(category, count)')
        self.con.execute('create table connections(connection, negative, positive)')
        self.con.commit()

    @staticmethod
    def check_word(word):
        """
        Checkea si la palabra no esta en la lista de negligibles, no es ni un hashtag ni un usuario
        y tiene una longitud entre 2 y 20
        :param word: (string) Palabra a checkear
        :return: (boolean) True si la palabra debe ser tenida en cuenta, False si no
        """
        if 2 < len(word) < 20:
            return False
        print(word)
        if word in Classifier.NEGLIGIBLE_WORDS:
            return False
        # TODO: Identificar y fijar error para poder eliminar el try-except
        try:
            if word[0] in ['@', '#']:
                return False
        except IndexError:
            return False
        return True

    @staticmethod
    def get_words(doc):
        """
        Divide un documento en palabras
        :param doc: (string) Documento a dividir
        :return: (dict) Diccionario con las palabras unicas en el documento 
        """
        splitter = re.compile('\\W*')  # Dividimos en cualquier caracter no alfanumerico
        words = [s.lower() for s in splitter.split(doc)
                 if Classifier.check_word(s.lower())]

        return dict([(w, 1) for w in words])

    @staticmethod
    def get_connections(doc, connection_range=1):
        """
        Divide un documento en las connexiones entre sus palabras
        :param doc: (string) Documento a dividir
        :param connection_range: (int) El rango en que crea las connexiones
        Ej: Si el rango es 1 juntara las palabras de 2 en 2, si el rango es 2 de 3 en 3, etc...
        :return: (dict) Diccionario de las connexiones unicas
        """

        splitter = re.compile('\\W*')
        words = [s.lower() for s in splitter.split(doc)
                 if Classifier.check_word(s.lower())]
        end = False
        connections = list()
        for i in range(len(words)):
            connection = ""
            for j in range(connection_range + 1):
                try:
                    connection += words[i + j] + "-"  # "-" entre palabras para facilitar su lectura
                except IndexError:
                    end = True
            if end:
                break
            connections.append(connection[:-1])

        return dict([(w, 1) for w in words])

    def inc_connection(self, f, cat):
        """
        Incrementa el valor de una categoria determinada de una connexion
        :param f: (string) Connexion 
        :param cat: (string) Categoria a incrementar
        """
        query = self.con.execute("UPDATE connections SET %s = %s + 1 WHERE connection = '%s'" % (cat, cat, f))
        if query.rowcount == 0:  # Si la connexion no esta en base de datos la guardamos
            self.con.execute("INSERT INTO connections(connection, negative, positive) VALUES(?,?,?)",
                             (
                                f,
                                self.CONNECTION_INIT_COUNTER + 1 if cat == 'negative' else self.CONNECTION_INIT_COUNTER,
                                self.CONNECTION_INIT_COUNTER + 1 if cat == 'positive' else self.CONNECTION_INIT_COUNTER
                             )
                             )

        self.con.commit()

    def get_connection_probability(self, f, cat):
        """
        La proablidad de que una connexion sea de una determinada categoria
        :param f: (string) Connexion 
        :param cat: (string) Categoria de la qual debe sacar-se la proabilidad
        :return: (float) Proablidad, puede ir del 0 al 2 ya que multiplicara la proablidad de la palabra
        """
        count = self.con.execute("select %s from connections where connection='%s'" % (cat, f)).fetchone()
        if count is None:  # Cuando la connexion aun no esta en la base de datos
            return 1
        else:
            count = count[0]
        total_count = 0
        for category in self.categories():
            count = self.con.execute("select %s from connections where connection='%s'" % (category, f)).fetchone()
            if count is None:  # Cuando la connexion aun no esta en la base de datos
                count = 0
            else:
                count = count[0]
            total_count += count

        return count*1.0/total_count * 2

    def incf(self, f, cat):
        """
        Incrementa la cuenta de una categoria en una determinada palabra
        :param f: (string) Palabra
        :param cat: (string) Categoria
        """
        query = self.con.execute("UPDATE words SET %s = %s + 1 WHERE word = '%s'" % (cat, cat, f))
        if query.rowcount == 0:  # Cuando la palabra aun no esta en la base de datos
            self.con.execute("INSERT INTO words(word, negative, positive) VALUES(?,?,?)",
                             (f, 1 if cat == 'negative' else 0, 1 if cat == 'positive' else 0))

        self.con.commit()

    def incc(self, cat):
        """
        Incrementa la cuenta de una determinada categoria
        :param cat: (string) Categoria
        """

        query = self.con.execute("UPDATE categories SET count = count + 1 WHERE category = '%s'" % cat)
        if query.rowcount == 0:  # Cuando la categoria aun no esta en la base de datos
            self.con.execute("INSERT INTO categories(category, count) VALUES(?,?)",
                             (cat, 1))

    def fcount(self, f, cat):
        """
        Devuelve la cuenta de una palabra en una determinada categoria
        :param f: (string) Palabra
        :param cat: (string) Categoria
        :return: (int) Numero de veces que la palabra aparece en la categoria
        """
        count = self.con.execute("select %s from words where word='%s'" % (cat, f)).fetchone()
        if count is None:  # Cuando la palabra aun no esta en la base de datos
            return 0
        return count[0]

    def catcount(self, cat):
        """
        Devuelve la cuenta de una categoria
        :param cat: (string) Categoria
        :return: (int) Numero de palabras en la categoria
        """
        count = self.con.execute("select count from categories where category='%s'" % cat).fetchone()[0]
        return count

    def totalcount(self):
        """
        :return: (int) Numero total de items guardados
        """
        count = 0
        for category in self.categories():
            count += self.con.execute("select sum(%s) from words" % category).fetchone()[0]
        return count

    def categories(self):
        """
        :return: (list) Lista de strings de todas las categorias
        """
        categories_list = list(self.con.execute("select category from categories").fetchall())

        return [c[0] for c in categories_list]

    def train(self, item, cat):
        """
        Entrena un determinado item perteneciente a una categoria
        :param item: (string) Item a entrenar
        :param cat: (string) Categoria a la que pertenece
        """
        features = self.get_words(item)
        # Increment the count for every feature with this category
        for f in features:
            self.incf(f, cat)
        for i in range(1, self.MAX_CONNECTION_RANGE):
            connections = self.get_connections(item, connection_range=i)
            for connection in connections:
                self.inc_connection(connection, cat)
        # Increment the count for this category
        self.incc(cat)

    def fprob(self, f, cat):
        """
        Calcula la proablidad de que una palabra pertenezca a una determinada categoria
        :param f: (string) Palabra
        :param cat: (string) Categoria
        :return: (float) Proablidad sobre 1
        """
        if self.catcount(cat) == 0: 
            return 0
        a = (self.fcount(f, cat) * 1.0)/self.catcount(cat)
        return a

    def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
        """
        Calcula una proablidad balanceada, para que el hecho de tener pocas apariciones de la palabra no de resultados
        muy extremos
        :param f: (string) Palabra
        :param cat: (string) Categoria
        :param prf: (method) Metodo para calcular la proablidad basica
        :param weight: (float) TODO
        :param ap: (float) TODO:
        :return: (float) Proablidad balanceada sobre 1
        """
        basicprob = prf(f, cat)
        totals = sum([self.fcount(f, c) for c in self.categories()])
        bp = ((weight*ap)+(totals*basicprob))/(weight+totals)
        return bp


class NaiveBayes(Classifier):
    """
    Clase NaiveBayes, superclase de Classifier, implementa los metodos de Bayes a esta subclase 
    """

    def __init__(self, dbname):
        """
        Inicia la subclasse Classifier con su base de datos i genera un diccionario de umbrales vacio
        :param dbname: (string) Nombre de las base de datos
        """
        Classifier.__init__(self, dbname)
        self.thresholds = {}

    def docprob(self, item, cat):
        """
        Calcula la proablidad de que un documento pertenezca a una categoria 
        :param item: (string) Documento a analizar
        :param cat: (string) Categoria
        :return: (float) Proablidad sobre 1
        """
        features = self.get_words(item)
        connections = list()
        for i in range(1, self.MAX_CONNECTION_RANGE):
            connections += self.get_connections(item, connection_range=i)

        p = 1
        for f in features:
            f_prob = self.weightedprob(f, cat, self.fprob)
            for connection in connections:
                f_prob *= self.get_connection_probability(connection[0], cat)
            p *= f_prob
        return p

    def prob(self, item, cat):
        """
        Devuelve la proablidad de que un documento pertenezca a una categoria
        multiplicado por la proablidad de esa categoria
        :param item: (string) Documento a analizar
        :param cat: (string) Categoria
        :return: (float) Proablidad sobre 1
        """
        catprob = (self.catcount(cat)*1.0)/self.totalcount()
        docprob = self.docprob(item, cat)
        return docprob*catprob

    def setthreshold(self, cat, t):
        self.thresholds[cat] = t

    def getthreshold(self, cat):
        if cat not in self.thresholds:
            return 1.0
        return self.thresholds[cat]

    def classify(self, item, default=None, get_probs=False):
        # si get_probs es True devolvera un diccionario de posibilidades, si no solo la mejor
        probs = {}
        # Find the category with the highest probability
        maximum = 0.0
        for cat in self.categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > maximum:
                maximum = probs[cat]
                best = cat
        # Make sure the probability exceeds threshold*next best
        for cat in probs:
            if cat == best:
                continue
            if probs[cat]*self.getthreshold(best) > probs[best]:
                return default
        self.train(item, best)
        if get_probs:
            return probs
        return best

    def train_data(self, csv_name, maximum=None, start_line=None):
        counter = 0
        success = 0
        error = 0
        with open(csv_name) as db:
            data = csv.reader(db)
            for line in data:
                if start_line:
                    if line[0].split(';')[0] < start_line:
                        continue
                string, category = line[0].split(';')[1],  line[0].split(';')[3]
                category = 'positive' if category == '1' else 'negative'
                predicted_category = self.classify(string)
                if predicted_category == category:
                    success += 1
                else:
                    error += 1
                if maximum:
                    counter += 1
                    print('%d/%d' % (counter, maximum))
                    if counter > maximum:
                        break
        return success*1.0/(success+error)

    def train_other(self, item, other_naive_bayes):
        category = self.classify(item)
        other_naive_bayes.train(item, category)


class SarcasmDetector(object):
    SARCASM_LIMITER = 50

    def __init__(self, twitter_bot, naive_bayes):
        self.larry = twitter_bot
        self.naives = naive_bayes
        self.thresholds = {}

    def is_sarcastic(self, tweet, user):
        global_score = self.naives.classify(tweet, get_probs=True)
        tmp_naive_bayes = NaiveBayes(user + '.bd')
        tmp_naive_bayes.make_tables()
        for tweet in self.larry.get_tweets_by_user(user):
            self.naives.train_other(tweet, tmp_naive_bayes)

        local_score = tmp_naive_bayes.classify(tweet, get_probs=True)

        global_percents = {
            'positive': global_score['positive']/(global_score['positive'] + global_score['negative']),
            'negative': global_score['negative'] / (global_score['positive'] + global_score['negative'])
        }
        local_percents = {
            'positive': local_score['positive'] / (local_score['positive'] + local_score['negative']),
            'negative': local_score['negative'] / (local_score['positive'] + local_score['negative'])
        }
        return (
                + abs(global_percents['positive'] - local_percents['positive'])
                + abs(global_percents['negative'] - local_percents['negative'])
            )
