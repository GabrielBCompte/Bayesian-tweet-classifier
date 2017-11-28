

if __name__ == '__main__':
    import docclass


    cl = docclass.NaiveBayes(docclass.getwords, 'test8.db')
    cl.maketables()
    cl.loadData()
    a = cl.prob('rabbit', 'positive')
    b = cl.prob('rabbit', 'negative')
    print "---"
    print a
    print b