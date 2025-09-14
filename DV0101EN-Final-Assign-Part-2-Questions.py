import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# --- Load the Data from URL ---
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"

try:
    # Use requests to fetch the content and pandas to read it
    response = requests.get(URL)
    response.raise_for_status() # Raises an exception for bad status codes
    df = pd.read_csv(StringIO(response.text))
except requests.exceptions.RequestException as e:
    print(f"Error fetching the data from URL: {e}")
    exit()


# --- Initialize the Dash App ---
app = dash.Dash(__name__)
app.title = "Automobile Sales Dashboard"

# --- Create the App Layout ---
app.layout = html.Div([
    # Page Header
    html.H1("Automobile Sales Statistics Dashboard",
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),

    # Dropdown Controls
    html.Div([
        html.Label("Select Report Type:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            placeholder='Select a report type',
            style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'textAlignLast': 'center'}
        )
    ]),
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in range(1980, 2014)],
            disabled=True, # Initially disabled
            placeholder='Select a year',
            style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'textAlignLast': 'center'}
        )
    ]),

    # Output Container for Graphs (2x2 Grid)
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flex-wrap': 'wrap'})
])


# --- Callback to Enable/Disable Year Dropdown ---
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    """Controls the state of the year dropdown based on the report type selection."""
    if selected_statistics == 'Yearly Statistics':
        return False  # Enable the year dropdown
    else:
        return True   # Disable the year dropdown


# --- Callback to Update Graphs ---
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    """Updates the 4-chart grid based on user selections."""

    if selected_statistics == 'Recession Period Statistics':
        # Filter data for recession periods
        recession_data = df[df['Recession'] == 1]

        # Plot 1: Average Automobile Sales Fluctuation Over Recession Period
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, x='Year', y='Automobile_Sales',
                           title="Average Automobile Sales Fluctuation Over Recession Period")
        )

        # Plot 2: Average Number of Vehicles Sold by Vehicle Type
        avg_vehicle_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(avg_vehicle_sales, x='Vehicle_Type', y='Automobile_Sales',
                          title="Average Number of Vehicles Sold by Vehicle Type")
        )

        # Plot 3: Total Expenditure Share by Vehicle Type During Recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type',
                          title="Total Expenditure Share by Vehicle Type During Recessions")
        )

        # Plot 4: Effect of Unemployment Rate on Vehicle Type and Sales
        unemp_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
             figure=px.bar(unemp_sales, x='Vehicle_Type', y='Automobile_Sales',
                           title="Effect of Unemployment Rate on Vehicle Type and Sales")
        )

        return [
            html.Div(className='chart-item', children=[R_chart1], style={'width': '50%'}),
            html.Div(className='chart-item', children=[R_chart2], style={'width': '50%'}),
            html.Div(className='chart-item', children=[R_chart3], style={'width': '50%'}),
            html.Div(className='chart-item', children=[R_chart4], style={'width': '50%'})
        ]

    elif selected_statistics == 'Yearly Statistics' and input_year is not None:
        # Filter data for the selected year
        yearly_data = df[df['Year'] == input_year]

        # Plot 1: Yearly Automobile Sales Using Line Chart for the Whole Period
        yas = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, x='Year', y='Automobile_Sales',
                           title="Yearly Average Automobile Sales")
        )

        # Plot 2: Total Monthly Automobile Sales Using Line Chart
        monthly_sales = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(monthly_sales, x='Month', y='Automobile_Sales',
                           title=f"Total Monthly Automobile Sales in {input_year}")
        )

        # Plot 3: Average Vehicles Sold by Vehicle Type in the Selected Year
        avg_vehicle_sales = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avg_vehicle_sales, x='Vehicle_Type', y='Automobile_Sales',
                          title=f'Average Vehicles Sold by Vehicle Type in {input_year}')
        )

        # Plot 4: Total Advertisement Expenditure for Each Vehicle Type
        ad_exp = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(ad_exp, values='Advertising_Expenditure', names='Vehicle_Type',
                          title=f'Total Advertisement Expenditure for Each Vehicle in {input_year}')
        )

        return [
            html.Div(className='chart-item', children=[Y_chart1], style={'width': '50%'}),
            html.Div(className='chart-item', children=[Y_chart2], style={'width': '50%'}),
            html.Div(className='chart-item', children=[Y_chart3], style={'width': '50%'}),
            html.Div(className='chart-item', children=[Y_chart4], style={'width': '50%'})
        ]

    else:
        return None


# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True)