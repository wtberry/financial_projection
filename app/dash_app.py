import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from finance_projection import financial_projection_with_loans
from datetime import datetime
from loan import Loan

# Initialize Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Financial Projection with Loans"),
    
    # Inputs for loans
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
        
        html.Button('Simulate', id='simulate_btn', n_clicks=0)
    ]),
    
    # Graph to display projection
    dcc.Graph(id='financial_projection_graph')
])

# Update graph when the user clicks the simulate button
@app.callback(
    Output('financial_projection_graph', 'figure'),
    [Input('simulate_btn', 'n_clicks')],
    [Input('loan_principal', 'value'),
     Input('loan_interest', 'value'),
     Input('loan_payment', 'value'),
     Input('loan_duration', 'value')]
)
def update_graph(n_clicks, loan_principal, loan_interest, loan_payment, loan_duration):
    # Simulate loan
    loans = [Loan(
        principal=loan_principal, 
        interest_rate=loan_interest/100, 
        payment=loan_payment, 
        start_date=datetime.now(), 
        duration=loan_duration,
        description="Custom Loan"
    )]

    initial_assets = 10000
    transactions = []
    recurring_transactions = []

    dates, balances, loan_balances = financial_projection_with_loans(
        initial_assets, transactions, recurring_transactions, loans
    )

    # Create traces for the graph
    balance_trace = go.Scatter(
        x=dates, y=balances, mode='lines+markers', name='Total Balance'
    )
    
    loan_traces = []
    for loan, loan_balance in loan_balances.items():
        loan_traces.append(
            go.Scatter(
                x=dates, y=loan_balance, mode='lines+markers', name=f"{loan} Remaining Balance"
            )
        )

    return {
        'data': [balance_trace] + loan_traces,
        'layout': go.Layout(
            title="Financial Projection",
            xaxis={'title': 'Date'},
            yaxis={'title': 'Balance'},
            hovermode='closest'
        )
    }

if __name__ == "__main__":
    app.run_server(debug=True)
