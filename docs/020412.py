[{'name':a[0], 'class':a[1], 'type':type(a[1]), 'num_methods':len([b for b in inspect.getmembers(a[1], inspect.ismethod) if not b[0].startswith('_') and not b[0] == '__init__' ]), 'mro':inspect.getmro(a[1])} for a in inspect.getmembers(MODULE,inspect.isclass) if inspect.getmembers(a[1], inspect.ismethod) and object in inspect.getmro(a[1])]

# target classes & top level functions to test
for MODULE in MODULES:
    classes = set()
    for a in inspect.getmembers(MODULE,inspect.isclass):
        if inspect.getmembers(a[1], inspect.ismethod) and \
            object in inspect.getmro(a[1]) and \
            [b for b in inspect.getmembers(a[1], inspect.ismethod) if not b[0].startswith('_')] and \
            hasattr(a[1], '__init__'):
            for i in inspect.getmro(a[1]):
                if inspect.getmodule(i) == MODULE:
                    classes.add(i)
    print '==',MODULE.__name__,'=='
    print classes
    print [b for b in inspect.getmembers(MODULE, inspect.isfunction or inspect.ismethod) if not b[0].startswith('_')]
    print

# top 20 PyPI packages by downloads
awk -F' ' '{ print $NF, $0 }' packages.txt | sort -r -n -k1 | head -n 20 | cut -d' ' -f 1,2

# create Python distribution (PasteScript)
paster create --template=basic_package Pyrulan

MODULES=[scipy,numpy,jinja2,setuptools,MySQLdb,unittest2,anyjson,kombu,processing,coverage,vnc2flv,ordereddict,yaml,openid,amqplib,OpenEXR,pep8]
