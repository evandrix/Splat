class Fruit:
    def __init__(self, sort):
        self.sort = sort
 
class Fruits:
    def __init__(self):
        self.sorts = {}
 
    def get_fruit(self, sort):
        if sort not in self.sorts:
            self.sorts[sort] = Fruit(sort)
 
        return self.sorts[sort]
 
if __name__ == '__main__':
    fruits = Fruits()
    print fruits.get_fruit('Apple')
    print fruits.get_fruit('Lime')
