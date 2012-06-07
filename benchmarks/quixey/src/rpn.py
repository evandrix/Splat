class Stack(object):
    def __init__(self):
        self.stack = []
    def push(self, item):
        self.stack.append(item)
    def pop(self):
        return self.stack.pop()

def rpn_eval(tokens):
    """
    Four-function calculator with input given in Reverse Polish Notation (RPN).
    Input:
        A list of values and operators encoded as floats and strings
    Precondition:
        all(
            isinstance(token, float) or token in ('+', '-', '*', '/') for token in tokens
        )
    """
    def op(symbol, a, b):
        return {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b
        }[symbol](a, b)
    stack = Stack()
    for token in tokens:
        if isinstance(token, float):
            stack.push(token)
        else:
            a = stack.pop()
            b = stack.pop()
            stack.push(
                op(token, b, a)
            )
    return stack.pop()

if __name__ == "__main__":
    assert rpn_eval([3.0, 5.0, '+', 2.0, '/']) == 4.0

