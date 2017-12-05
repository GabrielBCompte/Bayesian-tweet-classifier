import twitter
class TwitterSettings(object):
    """Aqui estaran todas las constantes que usaremos para el twitterBot
    estan en una classe diferente para poderlas cambiar mas facil"""
    ZONES = [] #Lista de ids de las zonas que vamos a analizar, unas 10 aprox, seguramente estados de USA por que sera mas sencillo
    # https://stackoverflow.com/questions/17633378/how-can-we-get-tweets-from-specific-country
    # Como en el link de arriba
    ZONE_TO_VERBOSE = {} # Diccionario para transformar de las zonas a un nombre comprensible
    #Ej: {'54ds564ds64aa': 'NEW YORK'}

class TwitterBot(object):
    """Este es nuestro bot de twitter, se encargara de leer 
    tweets por zonas(todas de habla inglesa) y asignar un porcentaje
    de tweets positivos, cosas que debeis saber:
    1: Lee por zonas solo porque es mas sencillo
    2: Depende de que twitter le de permiso para ello hacemos
    este proceso -> ""https://apps.twitter.com/ 
    3: Usamos la libreria de python-twitter, no es la oficial, la ha hecho este señor,
    leeros la documentacion -> https://python-twitter.readthedocs.io/en
    """
    def __init__(self):
        self.api = self.connect_api() #para acceder a la api, simplemente conectamos con lo que nos piden

    def connect_api(self):
        """Falta rellenar-lo"""
        api = twitter.Api(consumer_key=[consumer key],
                  consumer_secret=[consumer secret],
                  access_token_key=[access token],
                  access_token_secret=[access token secret])
        return api

    def get_tweets_by_zone(self, zone):
        return self.api.GetSearch(q="place: %s" % zone)['statuses']

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