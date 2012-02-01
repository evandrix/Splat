my_list = ['john', 'pat', 'gary', 'michael']
for i, name in enumerate(my_list):
#    print "iteration {iteration} is {name}".format(iteration=i, name=name)
    print "iteration %d is %s" % (i, name)