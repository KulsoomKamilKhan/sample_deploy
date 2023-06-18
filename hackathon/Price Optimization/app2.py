import dash
import re
import pandas as pd
import numpy as np
import dash_table
import logging
import plotly.graph_objects as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import Python.optimize_price
import Python.optimize_quantity
import Python.sentiment
import dash_daq as daq
import dash_table.FormatTemplate as FormatTemplate



group_colors = {"control": "light blue", "reference": "red"}

app = dash.Dash(
    __name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
)

dash.register_page(__name__)

server = app.server

# Load the data
df = pd.read_csv('Data/price-augmented.csv')
df.head(10)

# App Layout
app.layout = html.Div(
    children=[
        # Error Message
        html.Div(id="error-message"),
        # Top Banner
        html.Div(
            className="study-browser-banner row",
            children=[
                html.H2(className="h2-title",
                        children="PRODUCT PRICE OPTIMIZATION"),

                html.Div(
                    className="div-logo",
                    children=html.Img(
                        className="logo", src=app.get_asset_url("logo.png")
                    ),
                ),

            ],
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            className="padding-top-bot",
                            children=[
                                html.H6("OPTIMIZE"),
                                dcc.Dropdown(
                                    id="selected-var-opt",
                                    options=[
                                        {"label": "Price", "value": "price"},
                                        {"label": "Quantity", "value": "quantity"},
                                    ],
                                    value="price",
                                    clearable=False,
                                    searchable=False,
                                    className="dropdown",
                                ),
                            ],
                        ),
                        html.Br(),
                        html.Div(
                            className="padding-top-bot",
                            children=[
                                html.H6("OPTIMIZATION RANGE"),
                                html.Div(id="output-container-range-slider"),
                                dcc.RangeSlider(
                                    id="my-range-slider",
                                    min=0,
                                    max=500,
                                    step=1,
                                    marks={0: '0', 500: '500'},
                                    value=[200, 400]
                                ),
                            ],
                        ),
                        html.Br(),
                        html.Div(
                            className="padding-top-bot",
                            children=[
                                html.H6("FIXED COST"),
                                daq.NumericInput(
                                    id='selected-cost-opt',
                                    min=0,
                                    max=10000,
                                    value=80
                                ),
                            ],
                        ),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.H6("RECOMMENDATION:"),
                        html.Div(
                            id='id-insights', style={'color': 'DarkCyan', 'fontSize': 15}
                        ),
                        # html.Br(),
                        # html.Div(dbc.Button("GET CODE", color="primary", className="mr-1", href="https://github.com/amitvkulkarni/Data-Apps/tree/main/Price%20Optimization", target='_blank')),
                    ],
                    className="pretty_container two columns",
                    id="cross-filter-options",
                ),
            ],
        ),
        html.Div(
            [
                html.Div(
                    className="twelve columns card-left",
                    children=[
                        html.Div(
                            className="padding-top-bot",
                            children=[
                                html.H6("PRICE VS QUANTITY"),
                                dcc.Graph(id="lineChart2"),
                            ],
                        )
                    ],
                ),
            ],
            className="pretty_container four columns",
        ),
        html.Div(
            [
                html.Div(
                    className="twelve columns card-left",
                    children=[
                        html.Div(
                            className="padding-top-bot",
                            children=[
                                html.H6("MAXIMIZING REVENUE"),
                                dcc.Graph(id="lineChart1"),
                            ],
                        )
                    ],
                ),
            ],
            className="pretty_container four columns",
        ),
        html.Div(
            [
                html.Div(
                    className="twelve columns card-left",
                    children=[
                        html.Div(
                            className="padding-top-bot",
                            children=[
                                html.H6("SIMULATED RESULT"),
                                dash_table.DataTable(
                                    id='heatmap',
                                    columns=[
                                        {'name': 'Price', 'id': 'Price', 'type': 'numeric'},
                                        {'name': 'Revenue', 'id': 'Revenue', 'type': 'numeric'},
                                        {'name': 'Quantity', 'id': 'Quantity', 'type': 'numeric'},
                                    ],
                                    style_data_conditional=[
                                        {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                                        {'if': {'row_index': 0, 'column_id': 'Revenue'}, 'backgroundColor': 'dodgerblue', 'color': 'white'},
                                        {'if': {'row_index': 0, 'column_id': 'Price'}, 'backgroundColor': 'dodgerblue', 'color': 'white'},
                                        {'if': {'row_index': 0, 'column_id': 'Quantity'}, 'backgroundColor': 'dodgerblue', 'color': 'white'},
                                    ],
                                    style_header={
                                        'backgroundColor': 'rgb(230, 230, 230)',
                                        'fontWeight': 'bold',
                                    },
                                    style_data={
                                        'whiteSpace': 'normal',
                                        'height': 'auto',
                                    },
                                    editable=True,
                                    filter_action="native",
                                    sort_action="native",
                                    page_size=10,
                                ),
                            ],
                        )
                    ],
                ),
            ],
            className="pretty_container two columns",
        ),

                html.Div(
    className="pretty_container twelve columns",
    children=[
        html.Div(
            className="padding-top-bot",
            children=[
                html.H6("SENTIMENT ANALYSIS"),
                html.Div(id="text-display", style={'color': 'DarkCyan', 'fontSize': 15}),
            ],
        )
    ],
),
html.Div(
            className="pretty_container twelve columns",
            children=[
                html.Div(
                    className="padding-top-bot",
                    children=[
                        html.H6("PRICING STRATEGY"),
                        html.Div(
                            id="texts-display",
                            style={'color': 'DarkCyan', 'fontSize': 15}
                        ),
                        html.Div(
                            className="padding-top-bot",
                            children=[
                                html.H6("View Pricing Strategy for:"),
                                dcc.RadioItems(
                                    id="strategy-options",
                                    options=[
                                        {'label': 'Positive', 'value': 'positive'},
                                        {'label': 'Neutral', 'value': 'neutral'},
                                        {'label': 'Negative', 'value': 'negative'},
                                    ],
                                    value='positive',
                                    labelStyle={'display': 'inline-block'}
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),

       html.Div(
    [
        html.Div(
            className="padding-top-bot",
            style={'display': 'flex', 'flexDirection': 'row'},
            children=[
                html.Div(
                    className="pretty_container",
                    style={'display': 'inline-block', 'paddingRight': '10px'},
                    children=[
                        html.H6("COMPETITOR PRICES"),
                        dash_table.DataTable(
                            id='competitor-prices-table',
                            columns=[
                                {'name': 'Year', 'id': 'Year', 'type': 'numeric'},
                                {'name': 'Quarter', 'id': 'Quarter', 'type': 'numeric'},
                                {'name': 'Competitor Price', 'id': 'Competitor Price', 'type': 'numeric'},
                            ],
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold',
                            },
                            style_data_conditional=[
                                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                            ],
                            style_cell_conditional=[
                                {'if': {'column_id': 'Year'}, 'textAlign': 'left'},
                                {'if': {'column_id': 'Quarter'}, 'textAlign': 'left'},
                                {'if': {'column_id': 'Competitor Price'}, 'textAlign': 'right'},
                            ],
                            style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                            },
                            editable=False,
                            filter_action="native",
                            sort_action="native",
                            page_size=10,
                        ),
                    ]
                ),
                html.Div(
                    className="pretty_container",
                    style={'display': 'inline-block', 'paddingLeft': '10px'},
                    children=[
                        dcc.Graph(id="competitor-prices-graph"),
                    ]
                )
            ],
        )
    ],
    className="four columns",
)

    ]
)


@app.callback(
    Output("text-display", "children"),
    [Input("selected-var-opt", "value"),
     Input("my-range-slider", "value"),
     Input("selected-cost-opt", "value")]
)
def update_sentiment(var_opt, var_range, var_cost):
    overall_sentiment = Python.sentiment.get_overall_sentiment()
    return f"Target audience's perception towards the product: {overall_sentiment}"



@app.callback(
    Output('output-container-range-slider', 'children'),
    [Input('my-range-slider', 'value')]
)
def update_output(value):
    return "{}".format(value)


@app.callback(
    Output("texts-display", "children"),
    [Input("selected-var-opt", "value"),
     Input("my-range-slider", "value"),
     Input("selected-cost-opt", "value"),
     Input("strategy-options", "value")]
)
def update_sentiment(var_opt, var_range, var_cost, strategy_options):
    sentiment_string = Python.sentiment.get_overall_sentiment()
    start_index = sentiment_string.rfind("Overall sentiment: ") + len("Overall sentiment: ")
    end_index = sentiment_string.find(".", start_index)
    overall_sentiment = sentiment_string[start_index:end_index].strip()

    recommendations = []

    if strategy_options == 'positive' and overall_sentiment == "Positive":
        recommendations.append(f"Since the consumer views this product in a {overall_sentiment} light, we recommend increasing the price by 5%.")

    if strategy_options == 'neutral' and overall_sentiment == "Neutral":
        recommendations.append(f"Since the consumer views this product in a {overall_sentiment} light, we recommend keeping the price the same to test waters.")

    if strategy_options == 'negative' and overall_sentiment == "Negative":
        recommendations.append(f"Since the consumer views this product in a {overall_sentiment} light, we recommend decreasing the price by 5%.")

    if not recommendations:
        recommendations.append("No matching recommendations found.")

    return [
        html.P(f"Target audience's perception towards the product: {overall_sentiment}"),
        html.Div([html.P(rec) for rec in recommendations]),
    ]

@app.callback(
    [Output('competitor-prices-table', 'data'),
     Output('competitor-prices-graph', 'figure')],
    [Input('my-range-slider', 'value')]
)
def update_competitor_prices(selected_price_range):
    selected_min_price = selected_price_range[0]
    selected_max_price = selected_price_range[1]

    filtered_df = df[(df['Price'] >= selected_min_price) & (df['Price'] <= selected_max_price)]

    competitor_prices_data = filtered_df[['Year', 'Quarter', 'Competitor Price']].to_dict('records')

    competitor_prices_graph = px.line(filtered_df, x='Quarter', y='Competitor Price', color='Year')

    competitor_prices_graph.update_layout(
        xaxis=dict(title='Quarter'),
        yaxis=dict(title='Competitor Price'),
        title='Competitor Prices Comparison',
        showlegend=True,
        legend=dict(title='Year'),
        hovermode='x unified'
    )

    return competitor_prices_data, competitor_prices_graph



@app.callback(
    [
        Output("heatmap", 'data'),
        Output("lineChart1", 'figure'),
        Output("lineChart2", 'figure'),
        Output("id-insights", 'children'),
    ],
    [
        Input("selected-var-opt", "value"),
        Input("my-range-slider", "value"),
        Input("selected-cost-opt", "value"),
    ]
)
def update_output_All(var_opt, var_range, var_cost):

    try:
        if var_opt == 'price':
            res, fig_PriceVsRevenue, fig_PriceVsQuantity, opt_Price, opt_Revenue = Python.optimize_price.fun_optimize(
                var_opt, var_range, var_cost, df)
            res = np.round(res.sort_values(
                'Revenue', ascending=False), decimals=2)

            if opt_Revenue > 0:
                return [res.to_dict('records'), fig_PriceVsRevenue, fig_PriceVsQuantity,
                        f'The maximum revenue of {opt_Revenue} is achieved by optimizing {var_opt} of {opt_Price}, fixed cost of {var_cost} and optimization was carried for {var_opt} range between {var_range}']
            else:
                return [res.to_dict('records'), fig_PriceVsRevenue, fig_PriceVsQuantity,
                        f'For the fixed cost of {var_cost} and {var_opt} range between {var_range}, you will incur loss in revenue']

        else:
            res, fig_QuantityVsRevenue, fig_PriceVsQuantity, opt_Quantity, opt_Revenue = Python.optimize_quantity.fun_optimize(
                var_opt, var_range, var_cost, df)
            res = np.round(res.sort_values(
                'Revenue', ascending=False), decimals=2)

            if opt_Revenue > 0:
                return [res.to_dict('records'), fig_QuantityVsRevenue, fig_PriceVsQuantity,
                        f'The maximum revenue of {opt_Revenue} is achieved by optimizing {var_opt} of {opt_Quantity}, fixed cost of {var_cost} and optimization was carried for {var_opt} range between {var_range}']
            else:
                return [res.to_dict('records'), fig_QuantityVsRevenue, fig_PriceVsQuantity,
                        f'For the fixed cost of {var_cost} and {var_opt} range between {var_range}, you will incur loss in revenue']
    except Exception as e:
        logging.exception(str(e))
        return [dash.no_update, dash.no_update, dash.no_update, "Please provide valid inputs."]


if __name__ == "__main__":
    app.run_server(debug=True)

