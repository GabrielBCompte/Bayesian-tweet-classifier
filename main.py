

if __name__ == '__main__':
    import docclass
    from twitterbot import TwitterBot
    dc = docclass.NaiveBayes('test2.db')
    larry = TwitterBot(docclass=dc, db_name='twitter3.db')
    print(larry.get_all_data())
