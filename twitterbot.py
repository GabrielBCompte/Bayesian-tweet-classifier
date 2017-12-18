import twitter
from nltk.stem import PorterStemmer
from sqlite3 import dbapi2 as sqlite


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
    def __init__(self, docclass, db_name):
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
        tweets = self.get_tweets_by_user(name)
        return self.rate_tweets(tweets)

    def rate_trend(self, trend):
        tweets = self.get_tweets_by_trend(trend)
        return self.rate_tweets(tweets)

    def rate_tweets(self, tweets):
        results = dict()
        total_tweets = len(tweets)
        results['total'] = total_tweets
        for tweet in tweets:
            tweet_category = self.docclass.classify(tweet)
            try:
                results[tweet_category] += 1
            except KeyError:
                results[tweet_category] = 1
        for key in results.keys():
            results[key] = results[key] * 1.0 / total_tweets * 100

        return results

    def get_tweets_by_user(self, name):
        statuses = self.api.GetUserTimeline(screen_name=name, count=200)
        return self.clean_tweets(statuses)

    def get_tweets_by_trend(self, trend):
        statuses = self.api.GetSearch(term=trend, include_entities=True, count=100)
        return self.clean_tweets(statuses)

    def clean_tweets(self, statuses):
        tweets = list()
        for tweet in statuses:
            stemmed_tweet = ""
            for word in tweet.text.split(" "):
                stemmed_tweet += " " + self.stemmer.stem(word)
            tweets.append(stemmed_tweet)
        return tweets

    def get_current_trends(self):
        trends = self.api.GetTrendsWoeid(woeid=23424977)
        trends = [t.name for t in trends]
        return trends

    def update_trends_data(self):

        for trend in self.get_current_trends():
            self.save_date(trend, self.rate_trend(trend))


    def save_date(self, entity, results):
        """Esta funcion guardara en base de datos el score, la idea es tener una base de datos asi:
            |Zone|Score|Analized Tweets|"""
        print(entity)
        print(results)
        print("----------")

    def get_data(self, entity):
        pass