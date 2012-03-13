# old_python.py
class OldPython(object):
    def __init__(self, age):
        if age < 50:
            raise ValueError("%d isn't old" % age)
        self.age = age
 
    def hiss(self):
        if self.age < 60:
            return "sss sss"
        elif self.age < 70:
            return "SSss SSss"
        else:
            return "sss... *cough* *cough*"
