from datetime import datetime

class Transaction:
    def __init__(self, amount, date):
        self.amount = amount
        self.date = date

class RecurringTransaction:
    def __init__(self, amount, start_date, frequency):
        self.amount = amount
        self.start_date = start_date
        self.frequency = frequency  # Number of days between payments
