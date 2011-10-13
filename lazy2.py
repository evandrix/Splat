def get_db():
    db = getattr(get_db, 'db', db_connection())
    get_db.db = db
    return db
 
def func1():
    db = get_db()
    db.execute('SELECT * FROM things')    
 
def func2():
    db = get_db()
    db.execute('SELECT * FROM other_things')

class Lazy(type):
    def __init__(cls, name, bases, dict):
        super(Lazy, cls).__init__(name, bases, dict)    
        cls.instance = None
 
    def check_instance(cls):
        if cls.instance is None:
            if hasattr(cls, 'instantiate'):
                setattr(cls, 'instance', getattr(cls, 'instantiate')())
            else:
                raise Exception('Must implement the instantiate class method!')
 
    def __getattr__(cls, name):
        cls.check_instance()                
        return getattr(cls.instance, name)
 
    def __getitem__(cls, key):
        cls.check_instance()                
        return cls.instance.__getitem__(name)
 
    def __iter__(cls):
        cls.check_instance()                
        return cls.__iter__()
 
    def __contains__(self, item):
        cls.check_instance()                
        return cls.__contains__(item)
