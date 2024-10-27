import os

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

from projection import Projection, RecurringTransaction, OneTimeTransaction
from finance_projection import financial_projection_with_loans
#from transaction import RecurringTransaction, Transaction
from datetime import datetime
from loan import Loan

# Initialize Dash app
app = dash.Dash(
    name='finance_projection'
)

# Define layout
app.layout = html.Div([
    
    html.H1("Financial Projection with Loans"),

    # Date range selector (Start and End Date)
    html.Div([
        html.Label('Select Start Date:'),
        dcc.DatePickerRange(
            id='proj_date_range',
            min_date_allowed=datetime(2020, 1, 1),
            max_date_allowed=datetime(2030, 12, 31),
            initial_visible_month=datetime(2024, 11, 1),
            end_date=datetime(2024, 11, 25)
        )
    ], style={'display': 'inline-block', 'margin-right': '20px'}),


    # Input for initial assets
    html.Div([
        html.H3("Initial Assets"),
        dcc.Input(id='initial_assets', type='number', value=10000),
    ]),

    html.Hr(),

    # One-time Transaction Section
    html.Div([
        html.H3("One-time Transaction"),
        html.Button("Add One-time Transaction", id="add_one_time_btn", n_clicks=0),
        html.Div(id="one_time_transaction_container", children=[]),
    ]),

    # Recurring Transactions Section
    html.Div([
        html.H3("Recurring Transactions"),
        html.Button("Add Recurring Transaction", id="add_recurring_btn", n_clicks=0),
        html.Div(id="recurring_transaction_container", children=[]),
    ]),

    html.Hr(),
    
    # Loan inputs
    html.Div([
        html.H3("Loan Parameters"),
        html.Label("Principal:"),
        dcc.Input(id='loan_principal', type='number', value=5000),
        html.Label("Interest Rate (%):"),
        dcc.Input(id='loan_interest', type='number', value=5),
        html.Label("Monthly Payment:"),
        dcc.Input(id='loan_payment', type='number', value=200),
        html.Label("Duration (months):"),
        dcc.Input(id='loan_duration', type='number', value=24),
        html.Label("Start Date (YYYY/MM/DD):"),
        dcc.DatePickerSingle(
            id='loan_start_date',
            date=datetime(2024, 10, 1),  # Default start date
            display_format='YYYY-MM-DD',
            min_date_allowed=datetime(2020, 1, 1),
            max_date_allowed=datetime(2099, 12, 31)
        )
    ], style={'display': 'inline-block', 'margin-right': '20px'}),
    
    # Button to run the simulation
    html.Button('Simulate', id='simulate_btn', n_clicks=0),

    # Graph to display projection
    dcc.Graph(id='financial_projection_graph')
])

# Callback to dynamically add one-time transaction inputs
@app.callback(
    Output('one_time_transaction_container', 'children'),
    [Input('add_one_time_btn', 'n_clicks')],
    [State('one_time_transaction_container', 'children')]
)
def add_one_time_transaction(n_clicks, children):
    if n_clicks < 1:
        return children
    elif children is None:
        children = []
    new_transaction_input = html.Div([
        html.Label(f'Transaction {n_clicks}:'),
        dcc.Input(id={'type': 'one_time_amount', 'index': n_clicks}, type='number', placeholder='Amount'),
        dcc.DatePickerSingle(
            id={'type': 'one_time_date', 'index': n_clicks},
            date=datetime(2024, 10, 1),  # Default start date
            display_format='YYYY-MM-DD',
            min_date_allowed=datetime(2020, 1, 1),
            max_date_allowed=datetime(2099, 12, 31)
        )
    ], style={'display': 'inline-block', 'margin-right': '20px'})
    children.append(new_transaction_input)
    return children

# Callback to dynamically add recurring transaction inputs
@app.callback(
    Output('recurring_transaction_container', 'children'),
    [Input('add_recurring_btn', 'n_clicks')],
    [State('recurring_transaction_container', 'children')]
)
def add_recurring_transaction(n_clicks, children):
    if n_clicks < 1:
        return children
    elif children is None:
        children = []
    new_transaction_input = html.Div([
        html.Label(f'Recurring Transaction {n_clicks}:'),
        dcc.Input(id={'type': 'recurring_amount', 'index': n_clicks}, type='number', placeholder='Amount', value=380000),
        dcc.Dropdown(
            id={'type': 'recurring_frequency', 'index': n_clicks},
            options=[
                {'label': 'Daily', 'value': 'daily'},
                {'label': 'Weekly', 'value': 'weekly'},
                {'label': 'Monthly', 'value': 'monthly'},
                {'label': 'Yearly', 'value': 'yearly'}
            ],
            placeholder="Frequency",
            value='monthly'
        ),
        dcc.DatePickerSingle(
            id={'type': 'recurring_start_date', 'index': n_clicks},
            date=datetime(2024, 10, 1),
            display_format='YYYY-MM-DD'
        ),
        html.Br()
    ])
    children.append(new_transaction_input)
    return children


# Update graph when user clicks the simulate button
@app.callback(
    Output('financial_projection_graph', 'figure'),
    [
        Input('simulate_btn', 'n_clicks'),
        Input('proj_date_range', 'start_date'),  
        Input('proj_date_range', 'end_date'),
        Input('loan_start_date', 'date'),
    ],
    [State('initial_assets', 'value'),
     State({'type': 'one_time_amount', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'one_time_date', 'index': dash.dependencies.ALL}, 'date'),
     State({'type': 'recurring_amount', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'recurring_frequency', 'index': dash.dependencies.ALL}, 'value'),
     State({'type': 'recurring_start_date', 'index': dash.dependencies.ALL}, 'date'),
     State('loan_principal', 'value'),
     State('loan_interest', 'value'),   
     State('loan_payment', 'value'),
     State('loan_duration', 'value'),]
)
def update_graph(n_clicks, proj_start_date, proj_end_date, loan_start_date, initial_assets, one_time_amounts, one_time_dates, recurring_amounts, recurring_frequencies,
                 recurring_start_dates, loan_principal, loan_interest, loan_payment, loan_duration):
    
    print("all input:", n_clicks, proj_start_date, proj_end_date, loan_start_date, initial_assets, one_time_amounts, one_time_dates, recurring_amounts, recurring_frequencies,
                 recurring_start_dates, loan_principal, loan_interest, loan_payment, loan_duration)
    if proj_start_date is None or proj_end_date is None:
        return dash.no_update  # Don't update graph if dates are not selected
    
    print("one_itme", one_time_amounts, one_time_dates)
    print("recurring", recurring_amounts, recurring_frequencies, recurring_start_dates)

    # Ensure that one_time_amounts and one_time_dates are lists
    if not one_time_amounts or not one_time_dates:
        one_time_amounts = []
        one_time_dates = []

    # Ensure recurring transaction fields are lists
    if not recurring_amounts or not recurring_frequencies or not recurring_start_dates:
        recurring_amounts =  []
        recurring_frequencies =  []
        recurring_start_dates = []

    proj_start_date = datetime.fromisoformat(proj_start_date)
    proj_end_date = datetime.fromisoformat(proj_end_date)
    print("proj date:", type(proj_start_date))
    projection = Projection(proj_start_date, proj_end_date, initial_assets)


    # add one-time transactions
    for amount, date_str in zip(one_time_amounts, one_time_dates):
        date = datetime.strptime(date_str, '%Y-%m-%d')
        projection.add_transaction(OneTimeTransaction(amount, date))

    # add recurring transactions
    for amount, frequency_str, start_date_str in zip(recurring_amounts, recurring_frequencies, recurring_start_dates):
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        projection.add_transaction(RecurringTransaction(amount=amount, frequency=frequency_str, start_date=start_date))


    # Parse loan start date
    loan_start = datetime.strptime(loan_start_date, '%Y-%m-%dT00:00:00')

    # Simulate loan
    loans = [Loan(
        principal=loan_principal, 
        interest_rate=loan_interest / 100, 
        payment=loan_payment, 
        start_date=loan_start, 
        duration=loan_duration,
        description="Custom Loan"
    )]

    # print("loan", loans)
    # print("transactions",transactions)
    # print("recurring transactions:",recurring_transactions)

    # # Run financial projection
    # dates, balances, loan_balances = financial_projection_with_loans(
    #     initial_assets, transactions, recurring_transactions, loans, proj_start_date, proj_end_date
    # )
    results = projection.run_projection()
    dates, balances = [], []
    for date, balance in results:
        dates.append(date)
        balances.append(balance)
    # Create traces for the graph
    balance_trace = go.Scatter(
        x=dates, y=balances, mode='lines+markers', name='Total Balance'
    )

    # loan_traces = []
    # for loan, loan_balance in loan_balances.items():
    #     loan_traces.append(
    #         go.Scatter(
    #             x=dates, y=loan_balance, mode='lines+markers', name=f"{loan} Remaining Balance"
    #         )
    #     )

    return {
        'data': [balance_trace], #+ loan_traces,
        'layout': go.Layout(
            title="Financial Projection",
            xaxis={'title': 'Date'},
            yaxis={'title': 'Balance'},
            hovermode='closest'
        )
    }


# read host and port from environment variables
host = os.environ.get('HOST', 'localhost')
port = os.environ.get('PORT', 8050)

if __name__ == "__main__":
    app.run_server(host=host, port=port, debug=True)
