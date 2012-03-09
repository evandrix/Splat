def m4():
    parents, babies = (1, 1)
    while babies < 100:
        print 'This generation has {x} babies'.format(x=babies)
        parents, babies = (babies, parents + babies)
