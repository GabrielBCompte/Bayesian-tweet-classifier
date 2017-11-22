

if __name__ == '__main__':
    import docclass
    cl=docclass.naivebayes(docclass.getwords)
    docclass.sampletrain(cl)
    a = cl.prob('quick rabbit','good')
    b =     cl.prob('quick rabbit','bad')
    print a
    print b