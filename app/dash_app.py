import os
import streamlit as st
import plotly.graph_objs as go
from datetime import datetime

from projection import Projection, RecurringTransaction, OneTimeTransaction
from loan import Loan

# Initialize Streamlit app
st.set_page_config(page_title="Financial Projection with Loans")

st.title("Financial Projection with Loans")

# Date range selector (Start and End Date)
proj_start_date = st.date_input(
    "Select Start Date:",
    min_value=datetime(2020, 1, 1),
    max_value=datetime(2030, 12, 31),
    value=datetime(2024, 11, 1)
)
proj_end_date = st.date_input(
    "Select End Date:",
    min_value=proj_start_date,
    max_value=datetime(2030, 12, 31),
    value=datetime(2024, 11, 25)
)

# Input for initial assets
initial_assets = st.number_input("Initial Assets", value=10000)

st.sidebar.title("Transactions")

# One-time transactions
st.sidebar.header("One-time Transactions")
if 'one_time_transactions' not in st.session_state:
    st.session_state['one_time_transactions'] = []

if st.sidebar.button("Add One-time Transaction"):
    st.session_state['one_time_transactions'].append({
        "amount": st.sidebar.number_input("Amount", key=len(st.session_state['one_time_transactions'])),
        "date": st.sidebar.date_input("Date", value=datetime(2024, 10, 1), key=len(st.session_state['one_time_transactions'])),
    })

# Recurring Transactions
st.sidebar.header("Recurring Transactions")
if 'recurring_transactions' not in st.session_state:
    st.session_state['recurring_transactions'] = []

if st.sidebar.button("Add Recurring Transaction"):
    new_transaction = {
        "amount": st.sidebar.number_input("Amount", key=f"rec_amount_{len(st.session_state['recurring_transactions'])}"),
        "frequency": st.sidebar.selectbox(
            "Frequency", options=["weekly", "monthly", "yearly"],
            key=f"rec_freq_{len(st.session_state['recurring_transactions'])}"
        ),
        "start_date": st.sidebar.date_input(
            "Start Date", value=datetime(2024, 10, 1),
            key=f"rec_date_{len(st.session_state['recurring_transactions'])}"
        )
    }
    st.session_state['recurring_transactions'].append(new_transaction)

# Loan inputs
st.sidebar.header("Loan Parameters")
loan_principal = st.sidebar.number_input("Principal", value=5000)
loan_interest = st.sidebar.number_input("Interest Rate (%)", value=5)
loan_payment = st.sidebar.number_input("Monthly Payment", value=200)
loan_duration = st.sidebar.number_input("Duration (months)", value=24)
loan_start_date = st.sidebar.date_input("Start Date", value=datetime(2024, 10, 1))

# Run simulation button
if st.button("Simulate"):
    projection = Projection(proj_start_date, proj_end_date, initial_assets)

    # Add one-time transactions
    for t in st.session_state['one_time_transactions']:
        amount = t['amount']
        date = t['date']
        projection.add_transaction(OneTimeTransaction(amount, date))

    # Add recurring transactions
    for t in st.session_state['recurring_transactions']:
        amount = t['amount']
        frequency = t['frequency']
        start_date = t['start_date']
        projection.add_transaction(RecurringTransaction(amount, start_date, frequency))

    # Simulate loan
    loan_start = loan_start_date
    loans = [Loan(
        principal=loan_principal,
        interest_rate=loan_interest / 100,
        payment=loan_payment,
        start_date=loan_start,
        duration=loan_duration,
        description="Custom Loan"
    )]

    # Run financial projection
    results = projection.run_projection()
    dates, balances = [], []
    for date, balance in results:
        dates.append(date)
        balances.append(balance)

    # Create traces for the graph
    balance_trace = go.Scatter(
        x=dates, y=balances, mode='lines+markers', name='Total Balance'
    )

    # Display the graph
    fig = go.Figure(data=[balance_trace], layout=go.Layout(
        title="Financial Projection",
        xaxis={'title': 'Date'},
        yaxis={'title': 'Balance'},
        hovermode='closest'
    ))
    st.plotly_chart(fig)

