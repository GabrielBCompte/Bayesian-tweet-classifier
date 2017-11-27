

if __name__ == '__main__':
    import docclass
    cl = docclass.NaiveBayes(docclass.getwords, 'test2.db')
    docclass.sampletrain(cl)
    a = cl.prob('quick rabbit', 'positive')
    b = cl.prob('quick rabbit', 'negative')
    print a
    print b