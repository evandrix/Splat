class Hanoi(object):
    def __init__(self, unused):
        self.unused = 'unused'

    def __init__(self, unused1, unused2):
        self.unused1 = 3+4j

    def hanoi(self, height, start=1, end=3):
        steps = []
        if height > 0:
            helper = ({1, 2, 3} - {start} - {end}).pop()
            steps.extend(self.hanoi(height - 1, start, helper))
            steps.append((start, end))
            steps.extend(self.hanoi(height - 1, helper, end))
        return steps
