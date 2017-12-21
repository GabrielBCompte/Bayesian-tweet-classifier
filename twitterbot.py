import twitter
from nltk.stem import PorterStemmer
from sqlite3 import dbapi2 as sqlite

class TwitterBot(object):
	"""
	Clase del bot the twitter, se encarga de sacar tweets en tiempo real, hacerlos analizar
	y guardar los resultados en base de datos
	"""

	def __init__(self, docclass, db_name):
		"""
		Guarda la connexion a la api, el stemmer (para simplificar palabras)
		la clase que se encargara de clasificar y la connexion a la base de datos
		:param docclass: (object) clase clasificadora a usar
		:param db_name: (string) nombre de la base de datos
		"""
		self.api = self.connect_api()  #para acceder a la api, simplemente conectamos con lo que nos piden
		self.stemmer = PorterStemmer()
		self.docclass = docclass
		self.con = sqlite.connect(db_name)

	def make_tables(self):
		"""
		Crea las tablas necesarias para la base de datos
		"""
		self.con.execute('create table results(entity, negative, positive)')
		self.con.commit()

	def connect_api(self):
		"""
		Crea una connexion con la api de twitter
		return:(object) connexion
		"""
		api = twitter.Api(
			consumer_key='yNZ3txThPeRbxTsvOYT2LzKHF',
			consumer_secret='kJZwcMrWq8n0ZCPcwsFVveM8AouWLBfWC0WMrdrqFCjwW0zR7e',
			access_token_key='2836865725-I0wsvX1WZnl7HsZDX5IwrafWfmDMsvxQStIpGYj',
			access_token_secret='mMFDsgRzQhhH2oehYbDktoIJRQ7BfzvtjZvyA3sGvFQbq'
		)
		return api

	def rate_user(self, name):
		"""
		Devuelve los resultados de analizar un usuario
		param name: (string) Username
		return: (dict) Diccionario con la siguiente forma {
			'positive': porcentaje de tweets positivos
			'negative': porcentaje de tweets negativos  
		}
		"""
		tweets = self.get_tweets_by_user(name)
		return self.rate_tweets(tweets)

	def rate_trend(self, trend):
		"""
		Devuelve los resultados de analizar una tendencia
		param name: (string) hashtag
		return: (dict) Diccionario con la siguiente forma {
			'positive': porcentaje de tweets positivos
			'negative': porcentaje de tweets negativos  
		}
		"""
		tweets = self.get_tweets_by_trend(trend)
		return self.rate_tweets(tweets)

	def rate_tweets(self, tweets):
		"""
		Devuelve los resultados de analizar una lista de tweets
		param tweets: (list) lista de tweets
		return: (dict) Diccionario con la siguiente forma {
			'positive': porcentaje de tweets positivos
			'negative': porcentaje de tweets negativos  
		}
		"""
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

		for category in ['positive', 'negative']:
			if category not in results:
				results[category] = 0
		return results

	def get_tweets_by_user(self, name):
		"""
		Devuelve los ultimos tweets de un usuario
		param name: (string) Username
		return: (list) Lista de tweets(objects)
		"""
		statuses = self.api.GetUserTimeline(screen_name=name, count=200)
		return self.clean_tweets(statuses)

	def get_tweets_by_trend(self, trend):
		"""
		Devuelve los ultimos tweets de una tendencia
		param trend: (string) tendencia
		return: (list) Lista de tweets(objects)
		"""
		statuses = self.api.GetSearch(term=trend, include_entities=True, count=100)
		return self.clean_tweets(statuses)

	def clean_tweets(self, statuses):
		"""
		transforma una lista de objetos tweet en una lista de strings
		param statuses: (list) lista de objetos tweet
		return: (list) lista de strings con el texto de los tweets stemmeado
		"""
		tweets = list()
		for tweet in statuses:
			stemmed_tweet = ""
			for word in tweet.text.split(" "):
				stemmed_tweet += " " + self.stemmer.stem(word)
			tweets.append(stemmed_tweet)
		return tweets

	def get_current_trends(self):
		"""
		Devuelve las tendencias actuales en USA
		return (list): string list con los nombres de las tendencias
		"""
		trends = self.api.GetTrendsWoeid(woeid=23424977) # El woeid de USA
		trends = [t.name for t in trends]
		return trends

	def update_trends_data(self, maximum=None):
		"""
		Actualiza en base de datos los tweets positivos/negativos de las tendencias
		param maximum: (int) maximo de tendencias a analizar
		"""

		counter = 0
		for trend in self.get_current_trends():
			if maximum:
				counter += 1
				if counter > maximum:
					break
			self.save_date(trend, self.rate_trend(trend))

	def save_date(self, entity, results):
		"""
		Guarda en la base de datos de la entidad unos resultados
		:param entity: (string) Entidad de la cual guardar datos
		:param results: (dict) Diccionario con los resultados
		"""
		positive = results['positive']/100 * results['total']
		negative = results['negative']/100 * results['total']

		query = self.con.execute("UPDATE results SET positive = positive + %d WHERE entity = '%s'" % (positive, entity))
		if query.rowcount == 0:
			self.con.execute("INSERT INTO results(entity, negative, positive) VALUES(?,?,?)",
							 (entity, negative, positive))
		else:
			self.con.execute("UPDATE results SET negative = negative + %d WHERE entity = '%s'" % (negative, entity))

		self.con.commit()

	def get_entity_data(self, entity):
		"""
		Devuelve los datos sobre una entidad
		:param entity: (string) entidad
		:return: (dict) Diccionario con el siguiente formato 
		'nombre_entidad':{
			'positive': porcentage de tweets positivos
			'negative': porcentage de tweets negativos
		}
		"""
		positive = self.con.execute("select positive from results where entity='%s'" % entity).fetchone()
		if positive is None:
			return "No data for this entity"
		positive = positive[0]
		negative = self.con.execute("select negative from results where entity='%s'" % entity).fetchone()[0]

		return {
			entity: {
				'positive': (positive * 1.0 / (positive + negative)) * 100,
				'negative': (negative * 1.0 / (positive + negative)) * 100
			},
		}

	def get_all_entities(self):
		"""
		lista todas las entidades de la base de datos
		:return: (list) String list de las entidades
		"""
		if "'" in entity:
            		return "No data for this entity"
		entities_list = self.con.execute("select entity from results").fetchall()
		return entities_list

	def get_all_data(self):
		"""
		diccionario con todas las entidades y su respectiva data
		:return: (dict) Diccionario continiendo toda la data
		"""
		data = {}
		for entity in self.get_all_entities():
			entity_data = self.get_entity_data(entity)
			data.update(entity_data)
		return data

	def get_currents_trends_data(self):
		data = {}
		for entity in self.get_current_trends():
			entity_data = self.get_entity_data(entity)
			try:
				data.update(entity_data)
			except ValueError:
				pass
		return data
