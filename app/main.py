import os
import streamlit as st
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd

from projection import Projection, RecurringTransaction, OneTimeTransaction
from loan import Loan

# Initialize Streamlit app
st.set_page_config(page_title="Financial Projection with Loans")

st.title("Financial Projection with Loans and Transactions")

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

# data management
if "transactions" not in st.session_state:
    transactions = pd.DataFrame(columns=["amount", "date", "description", "type", "frequency"])
    st.session_state["transactions"] = transactions

transactions = st.session_state["transactions"]
# display transactions
st.header("Added Transactions")
st.dataframe(transactions)

# define callbacks to add transactions
def add_transaction():
    row = pd.DataFrame(
        {"amount": [st.session_state.input_amount],
         "date": [st.session_state.input_date],
         "description": [st.session_state.input_description],
         "type": [st.session_state.transaction_type],
         "frequency": [st.session_state.input_frequency]})
    st.session_state.transactions = pd.concat([st.session_state.transactions, row])

def add_frequency(transaction_columns):
    if "transaction_type" in st.session_state and st.session_state.transaction_type == "Recurring":
        with transaction_columns[4]:
            st.selectbox("Frequency", options=["daily", "weekly", "monthly", "yearly"], key="input_frequency")
    else:
        st.session_state.input_frequency = None

transaction_columns = st.columns(5)
with transaction_columns[0]:
    st.number_input("Amount", value=0, key="input_amount")
with transaction_columns[1]:
    st.date_input("Date", value=datetime(2024, 10, 1), key="input_date")
with transaction_columns[2]:
    st.text_input("Description", key="input_description")
with transaction_columns[3]:
    st.selectbox("Type", options=["One-time", "Recurring"], key="transaction_type", index=0, on_change=add_frequency(transaction_columns))
st.button("Add Transaction", on_click=add_transaction)


# # Loan inputs
# st.sidebar.header("Loan Parameters")
# loan_principal = st.sidebar.number_input("Principal", value=5000)
# loan_interest = st.sidebar.number_input("Interest Rate (%)", value=5)
# loan_payment = st.sidebar.number_input("Monthly Payment", value=200)
# loan_duration = st.sidebar.number_input("Duration (months)", value=24)
# loan_start_date = st.sidebar.date_input("Start Date", value=datetime(2024, 10, 1))

# Run simulation button
if st.button("Simulate"):
    projection = Projection(proj_start_date, proj_end_date, initial_assets)

    # Add one-time transactions
    for index, row in st.session_state.transactions.iterrows():
        if row["type"] == "One-time":
            amount = row["amount"]
            date = row["date"]
            description = row["description"]
            projection.add_transaction(OneTimeTransaction(amount, date, description))
        elif row["type"] == "Recurring":
            amount = row["amount"]
            frequency = row["frequency"]
            start_date = row["date"]
            description = row["description"]
            projection.add_transaction(RecurringTransaction(amount, start_date, frequency, description))


    # # Simulate loan
    # loan_start = loan_start_date
    # loans = [Loan(
    #     principal=loan_principal,
    #     interest_rate=loan_interest / 100,
    #     payment=loan_payment,
    #     start_date=loan_start,
    #     duration=loan_duration,
    #     description="Custom Loan"
    # )]

    # Run financial projection
    results = projection.run_projection()
    dates, balances, descriptions = [], [], []
    for date, balance, description in results:
        dates.append(date)
        balances.append(balance)
        descriptions.append(description)

    # Create traces for the graph
    balance_trace = go.Scatter(
        x=dates, y=balances, mode='lines+markers', name='Total Balance', text=descriptions
    )

    # Display the graph
    fig = go.Figure(data=[balance_trace], layout=go.Layout(
        title="Financial Projection",
        xaxis={'title': 'Date'},
        yaxis={'title': 'Balance'},
        hovermode='closest'
    ))
    st.plotly_chart(fig)

