### Import Libraries

import dash
from dash import dcc  # Dash Core Components
from dash import html  # Dash HTML Components
from dash.dependencies import Input, Output, State  # For callback functions
import plotly.graph_objs as go  # Plotly graph objects for visualizations

import pandas as pd  # Data manipulation
import datetime as dt  # Date and time handling

import yfinance as yf  # Yahoo Finance for stock data

import base64  # For encoding images

### Import Data

# List of tech giant stock tickers to download
tech_giant_tickers = [
    "AAPL", "MSFT", "GOOG", "AMZN", "META",
    "TSLA", "NVDA", "INTC", "ADBE", "NFLX", "CSCO",
    "PYPL", "AMD", "QCOM", "AVGO", "CRM", "ORCL"
]

# Download adjusted close prices for the tech giants from Yahoo Finance starting from 2019-01-01
df = yf.download(tech_giant_tickers, start='2019-01-01')['Adj Close']

### Set Dashboard Layout

# Initialize the Dash app
app = dash.Dash()

# Encode the logo image to base64
image_file = 'image/logos.png'
encoded = base64.b64encode(open(image_file, 'rb').read())

# Define the layout of the dashboard
app.layout = html.Div([
    # Header with title and logo
    html.Div([
        html.H2('Tech Giants Stock Price Trends', style={'fontFamily': 'helvetica', 'fontWeight': 700}),
        html.Img(src='data:image/png;base64,{}'.format(encoded.decode()), style={'height': '15%', 'width': '15%'})
    ], style={'width': '100%', 'textAlign': 'center'}),

    # Dropdown menu for selecting tickers
    html.Div([
        html.H4('Select ticker(s)', style={'fontFamily': 'helvetica', 'fontWeight': 500, 'color': '#808080'}),
        dcc.Dropdown(
            id='ticker-picker',
            options=[{'label': ticker, 'value': ticker} for ticker in tech_giant_tickers],
            multi=True,
            value=["AAPL", "GOOG", "AMZN", "META", "NVDA"]  # Default selected tickers
        )
    ], style={'width': '40%', 'display': 'inline-block', 'verticalAlign': 'top'}),

    # Date range picker for selecting the time period
    html.Div([
        html.H4('Select dates', style={'fontFamily': 'helvetica', 'fontWeight': 500, 'color': '#808080', 'verticalAlign': 'bottom'}),
        dcc.DatePickerRange(
            id='date-picker',
            min_date_allowed=min(df.index),  # Minimum date allowed
            max_date_allowed=max(df.index),  # Maximum date allowed
            initial_visible_month=max(df.index),  # Initial visible month in the calendar
            start_date=min(df.index),  # Default start date
            end_date=max(df.index)  # Default end date
        )
    ], style={'display': 'inline-block', 'marginLeft': '20px'}),

    # Submit button to update the graph with a header
    html.Div([
        html.H4('Click submit', style={'fontFamily': 'helvetica', 'fontWeight': 500, 'color': '#808080', 'verticalAlign': 'bottom'}),
        html.Button(
        id='button',
        n_clicks=0,  # Initial number of clicks
        children='Submit',
        style={'fontSize': 20}
    )], style={'display': 'inline-block', 'marginLeft': '20px'}),

    # Line chart to display stock prices
    dcc.Graph(
        id='line-chart',
        figure={
            'data': [go.Scatter(
                x=df.index,
                y=df[tick],
                name=tick,
                mode='lines'
            ) for tick in df.columns],
            'layout': go.Layout(
                xaxis={'title': 'Date'},
                yaxis={'title': 'Stock Price'},
                hovermode='closest'
            )
        }
    )
], style={'fontFamily': 'monospace'})

### Set Callback

# Define the callback function to update the graph based on user input
@app.callback(Output('line-chart', 'figure'),
              [Input('button', 'n_clicks')], #do not update the graph before user clicks submit
              [State('ticker-picker', 'value'),
               State('date-picker', 'start_date'),
               State('date-picker', 'end_date')]
              )
def update_graph(n_clicks, tickers, start_date, end_date):
    # Convert the selected start and end dates from string to date format
    start = dt.datetime.strptime(start_date[:10], '%Y-%m-%d').date()
    end = dt.datetime.strptime(end_date[:10], '%Y-%m-%d').date()
    
    # Filter the DataFrame for the selected date range
    data = df.loc[start:end]
    
    # Create the updated figure with the selected tickers and date range
    figure = {
        'data': [go.Scatter(
            x=data.index,
            y=data[tick],
            name=tick,
            mode='lines'
        ) for tick in tickers],
        'layout': go.Layout(
            xaxis={'title': 'Date'},
            yaxis={'title': 'Stock Price'},
            hovermode='closest',
            title='{} prices for the period from {} to {}'.format(tickers, start, end)
        )
    }
    return figure

### Run Server

if __name__ == '__main__':
    app.run_server()