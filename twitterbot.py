import twitter
from nltk.stem import PorterStemmer

class TwitterSettings(object):
    """Aqui estaran todas las constantes que usaremos para el twitterBot
    estan en una classe diferente para poderlas cambiar mas facil"""
    ZONES = [] #Lista de ids de las zonas que vamos a analizar, unas 10 aprox, seguramente estados de USA por que sera mas sencillo
    # https://stackoverflow.com/questions/17633378/how-can-we-get-tweets-from-specific-country
    # Como en el link de arriba
    ZONE_TO_VERBOSE = {} # Diccionario para transformar de las zonas a un nombre comprensible
    #Ej: {'54ds564ds64aa': 'NEW YORK'}

    PERSONS = []

class TwitterBot(object):
    """Este es nuestro bot de twitter, se encargara de leer 
    tweets por zonas(todas de habla inglesa) y asignar un porcentaje
    de tweets positivos, cosas que debeis saber:
    1: Lee por zonas solo porque es mas sencillo
    2: Depende de que twitter le de permiso para ello hacemos
    este proceso -> ""https://apps.twitter.com/ 
    3: Usamos la libreria de python-twitter, no es la oficial, la ha hecho este sr,
    leeros la documentacion -> https://python-twitter.readthedocs.io/en
    """
    def __init__(self, docclass):
        self.api = self.connect_api() #para acceder a la api, simplemente conectamos con lo que nos piden
        self.stemmer = PorterStemmer()
        self.docclass = docclass

    def connect_api(self):
        api = twitter.Api(
            consumer_key='yNZ3txThPeRbxTsvOYT2LzKHF',
            consumer_secret='kJZwcMrWq8n0ZCPcwsFVveM8AouWLBfWC0WMrdrqFCjwW0zR7e',
            access_token_key='2836865725-I0wsvX1WZnl7HsZDX5IwrafWfmDMsvxQStIpGYj',
            access_token_secret='mMFDsgRzQhhH2oehYbDktoIJRQ7BfzvtjZvyA3sGvFQbq'
        )
        return api

    def rate_user(self, name):
        results = dict()
        tweets = self.get_tweets_by_user(name)
        total_tweets = len(tweets)
        for tweet in tweets:
            tweet_category = self.docclass.classify(tweet)
            try:
                results[tweet_category] += 1
            except KeyError:
                results[tweet_category] = 1
        for key in results.keys():
            results[key] = results[key]*1.0/total_tweets * 100

        return results

    def get_tweets_by_user(self, name):
        # TODO: Mejorar, que no solo coja 20
        tweets = list()
        statuses = self.api.GetUserTimeline(screen_name=name)
        for tweet in statuses:
            stemmed_tweet = ""
            for word in tweet.text.split(" "):
                stemmed_tweet += " " + self.stemmer.stem(word)
            tweets.append(stemmed_tweet)
        return tweets

    def get_tweets_by_zone(self, zone):
        #TODO: Implementar
        return None

    def manage_tweets(self):
        for zone in TwitterSettings.ZONES:
            tweets = self.get_tweets_by_zone(zone)
            score = self.valore_tweets(tweets)
            self.save_data(zone, score)

    def valore_tweets(self, tweets):
        """Esta funcion cojera una serie de tweets, seguramente 100 y dara un porcentaje de
        positivos"""
        return 0

    def save_date(self, zone, score):
        """Esta funcion guardara en base de datos el score, la idea es tener una base de datos asi:
            |Zone|Score|Analized Tweets|"""