

if __name__ == '__main__':
    import docclass
    from twitterbot import TwitterBot
    dc = docclass.NaiveBayes('test19.db')

    larry = TwitterBot(docclass=dc, db_name='a')
    larry.update_trends_data()
