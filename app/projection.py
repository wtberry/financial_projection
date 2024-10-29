from datetime import datetime, timedelta

from abc import ABC, abstractmethod
from datetime import datetime

class Transaction(ABC):
    def __init__(self, amount: float, date: datetime, description: str = ""):
        self.amount = amount
        self.date = date
        self.description = description
    
    @abstractmethod
    def get_transaction_value(self, target_date: datetime):
        pass

    @abstractmethod
    def get_description(self, target_date: datetime):
        pass


class OneTimeTransaction(Transaction):
    def __init__(self, amount: float, date: datetime, description: str = ""):
        super().__init__(amount, date, description)
    
    def get_transaction_value(self, target_date: datetime):
        # Only include the transaction if it occurs before or on the target date
        return self.amount if self.date == target_date else 0.0

    def get_description(self, target_date):
        return self.description if self.date == target_date else ""

class RecurringTransaction(Transaction):
    def __init__(self, amount: float, start_date: datetime, frequency: str, description: str = ""):
        super().__init__(amount, start_date, description)
        self.frequency = frequency  # e.g., 'monthly', 'weekly', 'yearly'
    
    def get_transaction_value(self, target_date: datetime):
        """Check if the recurring transaction applies on the target date."""
        if self.date > target_date:
            return 0.0
        
        # Only return the transaction amount if the target date matches a recurrence
        if self._is_occurrence_on_date(target_date):
            return self.amount
        return 0.0
    
    def get_description(self, target_date):
        return self.description if self.date == target_date else ""
    
    def _is_occurrence_on_date(self, target_date: datetime):
        """Check if the transaction occurs on the target date."""
        if self.frequency == 'monthly':
            return target_date.day == self.date.day and target_date >= self.date
        elif self.frequency == 'weekly':
            return (target_date - self.date).days % 7 == 0 and target_date >= self.date
        elif self.frequency == 'yearly':
            return target_date.month == self.date.month and target_date.day == self.date.day and target_date >= self.date
        else:
            raise ValueError("Unsupported frequency")


class Projection:
    def __init__(self, start_date: datetime, end_date: datetime, initial_value: float):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_value = initial_value
        self.transactions = []
    
    def add_transaction(self, transaction: Transaction):
        """Add a transaction (either one-time or recurring) to the projection."""
        self.transactions.append(transaction)
    
    def run_projection(self):
        """Runs the projection over the selected date range."""
        balance = self.initial_value
        current_date = self.start_date
        projection_results = []

        while current_date <= self.end_date:
            # Calculate the sum of all transaction values on this date
            daily_total = sum(t.get_transaction_value(current_date) for t in self.transactions)
            balance += daily_total
            # get the description of the transaction
            description = "\n".join([t.get_description(current_date) for t in self.transactions])
            # Save the current date and balance for tracking purposes
            projection_results.append((current_date, balance, description))
            
            # Move to the next day (could adjust to weekly/monthly for efficiency)
            current_date += timedelta(days=1)

        return projection_results
