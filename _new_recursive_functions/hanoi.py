class Hanoi(object):
    def hanoi(self, height, start=1, end=3):
        steps = []
        if height > 0:
            helper = ({1, 2, 3} - {start} - {end}).pop()
            steps.extend(self.hanoi(height - 1, start, helper))
            steps.append((start, end))
            steps.extend(self.hanoi(height - 1, helper, end))
        return steps
