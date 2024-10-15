from datetime import timedelta
from datetime import datetime

def apply_loan_payments(loans, current_date, balance):
    for loan in loans:
        payment = loan.apply_payment(current_date)
        balance -= payment
    return balance

from datetime import datetime, timedelta

def financial_projection_with_loans(
    initial_assets, 
    transactions, 
    recurring_transactions, 
    loans, 
    start_date, 
    end_date
):
    # Ensure start and end dates are proper datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Create a list of dates between the start and end date
    projection_duration_days = (end_date - start_date).days + 1
    dates = [start_date + timedelta(days=i) for i in range(projection_duration_days)]
    
    # Initialize balances
    balances = [initial_assets]
    current_balance = initial_assets

    # Loan balances
    loan_balances = {str(loan): [loan.principal] for loan in loans}
    current_loan_balances = {loan: loan.principal for loan in loans}

    # Loop through each day in the projection period
    for current_date in dates[1:]:
        # Apply all recurring transactions
        for recurring_transaction in recurring_transactions:
            current_balance = recurring_transaction.apply(current_balance, current_date)

        # Apply all one-time transactions
        for transaction in transactions:
            current_balance = transaction.apply(current_balance, current_date)

        # Apply loan payments (only if the balance is > 0)
        for loan in loans:
            if current_loan_balances[loan] > 0:
                principal_payment, interest = loan.monthly_payment(current_loan_balances[loan])
                current_balance -= (principal_payment + interest)  # Deduct the loan payment
                current_loan_balances[loan] -= principal_payment

        # Append the current balance to the balances list
        balances.append(current_balance)

        # Update loan balances for graphing
        for loan in loans:
            loan_balances[str(loan)].append(current_loan_balances[loan])

    return dates, balances, loan_balances

