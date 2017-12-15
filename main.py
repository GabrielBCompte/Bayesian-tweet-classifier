

if __name__ == '__main__':
    import docclass
    from twitterbot import TwitterBot
    dc = docclass.NaiveBayes('test2.db')
    larry = TwitterBot(docclass=dc)
    sc = docclass.SarcasmDetector(naive_bayes=dc, twitter_bot=larry)
    print(sc.is_sarcastic('An announcement about the long-term future of Delicious: starting this fall, the site will offer free bookmarking to K-12 teachers worldwide',
                    'BarackObama'))
