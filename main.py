

if __name__ == '__main__':
    import docclass
    from twitterbot import TwitterBot
    from draw import Drawer
    dc = docclass.NaiveBayes('dbname')
    dc.make_tables() # No es necesario si se usa una base de datos ya entrenada
    dc.load_data('csv_name') # No es necesario si se usa una base de datos ya entrenada
    dw = Drawer()
    larry = TwitterBot(docclass=dc, db_name='twitter13.db')
    larry.make_tables()
    larry.update_trends_data(maximum=10)
    dw.draw_data(larry.get_currents_trends_data())
