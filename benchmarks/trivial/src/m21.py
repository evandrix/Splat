import random
guesses_made = 0
name = raw_input('Hello! What is your name?\n')
number = random.randint(1, 20)
print 'Well, {name}, I am thinking of a number between 1 and 20.'.format(name=name)
while guesses_made < 6:
    guess = int(raw_input('Take a guess: '))
    guesses_made += 1
    if guess < number:
        print 'Your guess is too low.'
    if guess > number:
        print 'Your guess is too high.'
    if guess == number:
        break
if guess == number:
    print 'Good job, {name}! You guessed my number in {guesses} guesses!'.format(name=name, guesses=guesses_made)
else:
    print 'Nope. The number I was thinking of was {number}'.format(number=number)
