from datetime import datetime

class Loan:
    def __init__(self, principal, interest_rate, payment, start_date, duration, description=""):
        self.principal = principal
        self.interest_rate = interest_rate
        self.payment = payment
        self.start_date = start_date
        self.duration = duration
        self.description = description
        self.remaining_principal = principal

    def apply_payment(self, current_date):
        if self.remaining_principal <= 0 or current_date < self.start_date:
            return 0  # Loan is fully paid or payments have not started yet

        # Calculate monthly interest
        monthly_interest = self.remaining_principal * (self.interest_rate / 12)
        principal_payment = self.payment - monthly_interest
        self.remaining_principal = max(self.remaining_principal - principal_payment, 0)
        
        return self.payment
