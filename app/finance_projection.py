from datetime import timedelta
from datetime import datetime

def apply_loan_payments(loans, current_date, balance):
    for loan in loans:
        payment = loan.apply_payment(current_date)
        balance -= payment
    return balance

def financial_projection_with_loans(initial_assets, transactions, recurring_transactions, loans, months=12):
    dates = []
    balances = []
    loan_balances = {loan.description: [] for loan in loans}

    current_date = datetime.now()
    balance = initial_assets

    for month in range(months):
        dates.append(current_date)

        # Apply recurring transactions
        for recurring in recurring_transactions:
            if (current_date - recurring.start_date).days % recurring.frequency == 0:
                balance += recurring.amount

        # Apply one-time transactions
        for transaction in transactions:
            if transaction.date.month == current_date.month and transaction.date.year == current_date.year:
                balance += transaction.amount

        # Apply loan payments
        balance = apply_loan_payments(loans, current_date, balance)
        balances.append(balance)

        for loan in loans:
            loan_balances[loan.description].append(loan.remaining_principal)

        # Move to the next month
        current_date += timedelta(days=30)

    return dates, balances, loan_balances
