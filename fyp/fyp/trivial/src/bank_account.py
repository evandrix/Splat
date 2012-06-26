class BankAccount(object):
    def __init__(self, initial_balance=0):
        self.balance = initial_balance
    def deposit(self, amount):
        self.balance += amount
    def withdraw(self, amount):
        self.balance -= amount
    def overdrawn(self):
        return self.balance < 0

def main():
    my_account = BankAccount(15)
    my_account.withdraw(5)
    return my_account.balance

if __name__ == "__main__":
    main()

