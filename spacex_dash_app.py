import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load your data
URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv'
spacex_df=pd.read_csv(URL)
# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard"),

    # Dropdown for selecting launch site
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()
        ] + [{'label': 'ALL', 'value': 'ALL'}],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    # Pie chart for success rate
    dcc.Graph(id='success-pie-chart'),

    # Range slider for payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[0, 10000],
        marks={i: str(i) for i in range(0, 10001, 1000)},
        tooltip={"placement": "bottom", "always_visible": True}
    ),

    # Scatter plot for payload vs. success
    dcc.Graph(id='success-payload-scatter-chart')
])

# Callback to update the pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Group by launch site and count success/failure
        success_counts = spacex_df.groupby('Launch Site')['class'].value_counts().unstack().fillna(0)
        success_counts = success_counts.rename(columns={0: 'Failure', 1: 'Success'})
        success_counts['Total'] = success_counts['Success'] + success_counts['Failure']
        fig = px.pie(
            success_counts.reset_index(),
            names='Launch Site',
            values='Total',
            title='Launch Success Distribution for All Sites',
            labels={'Launch Site': 'Site', 'Total': 'Total Launches'}
        )
    else:
        # Filter dataframe for the selected site
        data = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = data['class'].value_counts()
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title=f'Launch Success Distribution for {selected_site}',
            labels={'index': 'Success/Failure', 'values': 'Count'}
        )

    return fig

# Callback to update the scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filter dataframe based on selected site
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

    # Filter based on payload range
    min_payload, max_payload = payload_range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min_payload) &
                              (filtered_df['Payload Mass (kg)'] <= max_payload)]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version',  # Ensure this is the correct column name
        title=f'Payload vs. Success for {selected_site}' if selected_site != 'ALL' else 'Payload vs. Success for All Sites',
        labels={'class': 'Success (1) / Failure (0)', 'Payload Mass (kg)': 'Payload Mass (kg)'}
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port = 8051, debug=True)


