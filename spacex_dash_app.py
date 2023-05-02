# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default select value is for ALL sites
        dcc.Dropdown(
            id="site-dropdown",
            options=[
                {"label": "All Sites", "value": "ALL"},
                *[
                    {"label": launch_site, "value": launch_site}
                    for launch_site in spacex_df["Launch Site"].unique()
                ],
            ],
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),
        html.Br(),
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10_000,
            step=1000,
            value=[min_payload, max_payload],
        ),
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Success Launches By Site",
        )
        return fig
    else:
        filtered_df = (
            spacex_df[spacex_df["Launch Site"] == entered_site]
            .groupby("class")
            .size()
            .reset_index(name="Number of launches")
        )
        # return the outcomes piechart for a selected site
        fig = px.pie(
            filtered_df,
            values="Number of launches",
            names="class",
            title=f"Total Success Launches for site {entered_site}",
        )
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        [
            Input(component_id="site-dropdown", component_property="value"),
            Input(component_id="payload-slider", component_property="value"),
        ],
    ],
)
def get_success_payload_scatter_plot(entered_site, payload_range):
    payload_range_min, payload_range_max = payload_range
    # filter by launch site
    if entered_site == "ALL":
        filtered_df = spacex_df
        title = "Correlation between Payload and Success for all Sites"
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        title = f"Correlation between Payload and Success for site {entered_site}"
    # filter by payload range
    filtered_df = filtered_df[
        (payload_range_min <= filtered_df["Payload Mass (kg)"])
        & (filtered_df["Payload Mass (kg)"] <= payload_range_max)
    ]
    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title,
    )
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server()
