from datetime import datetime
from projection import Projection, OneTimeTransaction, RecurringTransaction

# Initial parameters
start_date = datetime(2024, 10, 20)
end_date = datetime(2025, 1, 30)
initial_asset_value = 100000.0  # Starting balance

# Create projection
projection = Projection(start_date, end_date, initial_asset_value)

# Add one-time and recurring transactions
one_time = OneTimeTransaction(120000, datetime(2024, 11, 15), "Bonus")
one_time_daichi = OneTimeTransaction(50000, datetime(2024, 11, 30), "Daichi")
recurring_rent = RecurringTransaction(-240000, datetime(2024, 10, 26), "monthly", "Rent")
recurring_salary = RecurringTransaction(380000, datetime(2024, 10, 25), "monthly", "Salary")

projection.add_transaction(one_time)
projection.add_transaction(recurring_rent)
projection.add_transaction(recurring_salary)

# Run the projection
results = projection.run_projection()

# Output results (date and balance)
for date, balance in results:
    print(f"Date: {date.strftime('%Y-%m-%d')}, Balance: {balance}")
