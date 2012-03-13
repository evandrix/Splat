# old_nest.py
from old_python import OldPython
 
class OldNest(object):
    def __init__(self, ages):
        self.pythons = []
        for age in ages:
            try:
                self.pythons.append(OldPython(age))
            except ValueError:
                pass # Ignore the youngsters.
    def put_hand(self):
        return '\n'.join([python.hiss() for python in self.pythons])
