"""Importing the required libraries"""

from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd

# import plotly.offline as pyo
import plotly.graph_objs as go

import plotly.express as px


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
iso_alpha = ['USA', 'IND', 'BRA', 'FRA', 'TUR', 'RUS', 'GBR', 'ITA', 'ARG', 'ESP', 'COL', 'DEU', 'IRN', 'POL', 'MEX', 'UKR', 'PER', 'IDN', 'ZAF', 'NLD', 'CZE', 'CHL', 'CAN', 'PHL', 'IRQ', 'SWE', 'ROU', 'BEL', 'PAK', 'PRT', 'ISR', 'BGD', 'HUN', 'JPN', 'JOR', 'SRB', 'CHE', 'MYS', 'AUT', 'NPL', 'ARE', 'LBN', 'MAR', 'SAU', 'ECU', 'BGR', 'GRC', 'BLR', 'BOL', 'KAZ', 'SVK', 'PRY', 'PAN', 'TUN', 'HRV', 'GEO', 'CRI', 'URY', 'AZE', 'KWT', 'PSE', 'DOM', 'DNK', 'LTU', 'ETH', 'EGY', 'GTM', 'IRL', 'BHR', 'SVN', 'MDA', 'VEN', 'HND', 'OMN', 'ARM', 'LKA', 'QAT', 'BIH', 'THA', 'LBY', 'KEN', 'NGA', 'CUB', '', 'KOR', 'MMR', 'LVA', 'DZA', 'ALB', 'EST', 'NOR', 'ZMB', 'KGZ', 'UZB', 'MNE', 'GHA', 'FIN', 'AFG', 'CMR', 'SLV', 'MNG', 'CYP', 'MOZ', 'LUX', 'MDV', 'NAM', 'SGP', 'UGA', 'BWA', 'JAM', 'CIV', 'SEN', 'MDG', 'ZWE', 'KHM', 'AGO', 'SDN', 'DRC', 'MWI', 'CPV', 'MLT', 'AUS', 'TTO', 'RWA', '', 'GUF', 'SYR', 'GAB', 'GIN', 'MYT', 'MRT', 'PYF', 'SWZ', 'GUY', 'SUR', 'PNG', 'GLP', 'HTI', 'SOM', 'MLI', 'AND', 'TGO', 'BFA', 'SYC', 'BLZ', 'TWN', 'CUW', 'MTQ', 'BHS', 'COG', 'HKG', 'DJI', 'ABW', 'LSO', 'SSD', 'VNM', 'GNQ', 'TLS', 'BEN', 'NIC', 'CAR', 'YEM', 'ISL', 'GMB', 'NER', 'LCA', 'SMR', 'BDI', 'TCD', 'ERI', 'SLE', 'GIB', '', 'BRB', 'COM', 'GNB', 'LIE', 'NZL', 'MCO', 'SXM', 'BMU', 'LBR', 'TCA', 'STP', '', 'MAF', 'LAO', 'BTN', '', 'IMN', 'MUS', 'AIA', 'FJI', '', 'FRO', 'CYM', 'TZA', 'BRN', 'BVI', 'DMA', 'KNA', 'NCL', 'MAC', 'GRL']

"""Building the functions required to scrape the website"""

# ---------------------------------------------------------------------------

def get_country_data(country_line):
    """
    This function formats a given input line parsed from an html page.

    Parameters:
        country_line : str
            it is a row table row, that contains the data.

    Returns:
        line : list
            A list containing all the useful information retrieved.
    """
    import re
    line = country_line.strip().split("\n")
    line.pop(0)
    for i, element in zip(range(len(line)), line):
        if re.search("[1-9]+", element):
            line[i] = float(''.join(line[i].strip('+').split(",")))
        else:
            pass

    return line[:-1]


def get_column_names(tr):
    """
    This function return a well formatted list for the column names.
    """
    line = tr.strip("\n#").strip().split("\n")
    line[12] += line[13]
    line.pop(14)
    line.pop(13)
    return line[1:-1]
"""
    This function scrapes the data from the target website and returns a well formatted dict that contains information about every given country.
    """


def scrape_corona_data():
    from collections import defaultdict  # Importing the defaultdict model, that will be used to store the information while scraping the website
    countries_data = defaultdict(dict)
    coronameter = requests.get("https://www.worldometers.info/coronavirus/")  # requesting the index page from the server, it is also where our information resides
    bscorona = BeautifulSoup(coronameter.text, "lxml")  # parsing the webpage to a beautifulsoup object.
    corona_table = bscorona.find("table", id="main_table_countries_today")  # selecting the table where our data is contained.
    print(corona_table.tr.text)
    column_names = get_column_names(corona_table.tr.text)
    print(column_names)
    for tr in corona_table.find_all("tr", {"style": ""})[2:-2]:
        line = get_country_data(tr.text)
        countries_data[line[0]] = dict(zip(column_names, line[1:]))
    return countries_data


def replace_nan(data):
    """
    This function replaces empty or N/A values with np.nan so that it can be easier to manipulate the data later on.
    """
    for col in data.columns:
        data[col].replace(["N/A", "", " "], np.nan, inplace=True)


def create_clean_dataframe(countries_data):
    """
    This function takes a dict object and create a clean well formatted dataframe.

    Parameters:
        countries_data : dict object
            The dict that contains the countries data.
    Returns:
        data : dataframe
            Well formatted dataframe.
    """
    data = pd.DataFrame(countries_data).transpose()
    replace_nan(data)
    return data


"""Building the plotting functions"""

# ---------------------------------------------------------------------------

def plot_continent_data(data, keyword):
    """ This function creates a Figure from continental data.
    Parameters:
        data : dataframe
            The whole dataset.
        keyword : str
            The keyword used to define the figure wanted, the available keyword : {"Total", "New"}
    Returns:
        fig : Figure
            The figure that will be drawed on plotly. """
    colors = ["#031cfc", "#24b514", "#d11d1d"]
    if keyword == "New":
        cols = ["NewCases", "NewRecovered", "NewDeaths"]
    else:
        cols = ["TotalCases", "TotalRecovered", "TotalDeaths"]
    ## ==================== Graph Object ================
    #plot_data = []
    """for col, color in zip(cols, colors):
        plot_data.append(go.Bar(x=res.index.to_list(), y=res[col], name=col, marker=dict(color=color)))
    layout = go.Layout(title=f"Corona {keyword} Cases/Recovered/Deaths",
                       xaxis=dict(title="Continents"),
                       yaxis=dict(title="Cases per Continent"))
    fig = go.Figure(data=plot_data, layout=layout)"""
    ## ================= Plotly express =================
    res = pd.DataFrame()
    for col in cols:
        res[col] = data.groupby("Continent")[col].sum()
    title = f"Corona {keyword} Cases/Recovered/Deaths"
    fig = px.bar(res, x=res.index.to_list(), y=cols, barmode='group', title=title,
                 color_discrete_sequence=colors, labels={"x": "Continents"})
    fig.update_yaxes(title_text="Cases per Continent", secondary_y=False)
    return fig


def get_continent_sorted_data(data, continent, sortedby="TotalCases", ascending=False):
    """
    This function creates a sorted dataframe related to a continent and sorted by a columns.

    Parameters:
        data : dataframe
            The whole dataset.
        continent : str
            The continent we want to get the data from.
        sortedby : str, Default="TotalCases"
            The name of the column we want to sort by.
        ascending : Boolean, Default=False
            Either we want to sort in an ascending order or descending order.
    Returns:
        groupedbydata : dataframe
            A dataframe groupedby the continent.
    """
    return data.groupby("Continent").get_group(continent).sort_values(by=sortedby, ascending=ascending).reset_index()


def get_top_k_countries(data, k_countries=10, sortedby="TotalCases", ascending=False):
    """
    This function creates a k-len dataframe sorted by a key.

    Parameters:
        data : dataframe.
            The whole dataset.
        k_countries : int, Default=10
            The number of countries you want to plot.
        sortedby : str, Default="TotalCases".
            The column name we want to sort the data by
        ascending : Boolean, Default=False
            Either we want to sort in an ascending order or descending order.

    Returns:
        data : dataframe
            The k_contries lines dataframe sortedby the key given and in the wanted order.
    """
    return data.sort_values(by=sortedby, ascending=ascending).iloc[:k_countries]


def plot_top_k_countries(n_countries, sortby):
    """This function returns a figure where a number of countries are sorted by the value that resides in sortby."""
    res = get_top_k_countries(data, n_countries, sortby)
    ## ==================== Graph Object ================
    """plot_data = []
    plot_data.append(go.Bar(x=res.index.to_list(), y=res[sortby], name=sortby))
    layout = go.Layout(title=f"Top Countries orderedby {sortby}",
                       xaxis=dict(title="Countries"),
                       yaxis=dict(title=f"{sortby}"))
    fig = go.Figure(data=plot_data, layout=layout)"""
     ##================= Plotly express =================
    title = f"Top Countries ordered by {sortby}"
    fig = px.bar(res, x=res.index.to_list(), y=sortby, title=title, labels={'x': "Countries"})
    fig.update_yaxes(title_text=sortby, secondary_y=False)
    return fig


def plot_boxplots(data, keyword="Deaths/1M pop"):
    """This function returns a figure of the boxplot related to each continent in regards to the keyword."""
    plot_data = []
    grouped_data = data.groupby("Continent")
    continents = data["Continent"].value_counts().index.to_list()
    ## ==================== Graph Object ================
    """for continent in continents:
        plot_data.append(go.Box(y=grouped_data.get_group(continent)[keyword], name=continent))
    layout = go.Layout(title=f"Boxplots using {keyword}",
                       xaxis=dict(title="Continents"),
                       yaxis=dict(title=f"{keyword}"))
    fig = go.Figure(data=plot_data, layout=layout)
    fig = px.box(grouped_data, y=grouped_data.get_group(continents)[keyword], name=continents)
    """
    ## ================= Plotly express =================
    y = {}
    for continent in continents:
        y[continent] = grouped_data.get_group(continent)[keyword]
    labels = {"variable": "Continents", "value": keyword}
    fig = px.box(y, color="variable", title=f"Boxplot using {keyword}", labels=labels)
    return fig


def plot_pie_chart(n_countries, sortby):
    """ This function plot a pie chart of the top K countries based on number of active cases / critical cases"""
    res = get_top_k_countries(data, n_countries, sortby)
    fig = px.pie(res, values=sortby, names=res.index)
    return fig


def geo_plot(data, keyword):
    data = data.fillna(0)
    data = data[data.index != "Western Sahara"]  ## Removing the inexistant country called Western Sahara
    fig = px.scatter_geo(data, locations=iso_alpha, color="Continent", hover_name=data.index,
                         size=data[keyword].to_list(), projection="natural earth")
    return fig

def init_figure():
    """This function initiate all the needed figure to start the app."""
    return plot_continent_data(data, keyword="New"), plot_top_k_countries(10, "TotalCases"),\
           plot_boxplots(data), plot_pie_chart(5, "ActiveCases"), geo_plot(data, "TotalCases")


"""Initiale Figures"""
# ---------------------------------------------------------------------------

countries_data = scrape_corona_data()
print("============================")
data = create_clean_dataframe(countries_data)

init_continent_fig, init_k_countries_plot, init_box_fig, init_pie_chart, init_geo_plot = init_figure()



"""Building the app"""
# ---------------------------------------------------------------------------

# Initializing the app
app = dash.Dash(__name__)
server = app.server

# Building the app layout
app.layout = html.Div([
    html.H1("Corona Tracker DashBoard", style={"text-align": "center"}),
    html.Br(),
    html.Div([
        html.Br(),
        html.H2("Corona Cases/Recovered/Deaths by Continent", style={"text-align": "center"}),
        html.Br(),
        dcc.Dropdown(id="select_keyword",
                     options=[
                         dict(label="Today's Data", value="New"),
                         dict(label="Total Data", value="Total")],
                     multi=False,
                     value="New",
                     style={"width": "40%"}
                     ),

        dcc.Graph(id="continent_corona_bar", figure=init_continent_fig)
    ]),

    html.Div([
        html.Br(),
        html.H2("Visualize Countries by attribute.", style={"text-align": "center"}),
        html.Br(),
        dcc.Dropdown(id="select_attribute",
                     options=[
                         dict(label="Total Cases", value='TotalCases'),
                         dict(label="New Cases", value='NewCases'),
                         dict(label="Total Cases per 1M population", value='Tot Cases/1M pop'),
                         dict(label="Active Cases", value='ActiveCases'),
                         dict(label="Serious, Critical Cases", value='Serious,Critical'),
                         dict(label="Total Deaths", value='TotalDeaths'),
                         dict(label="New Deaths", value='NewDeaths'),
                         dict(label="Deaths per 1M population", value='Deaths/1M pop'),
                         dict(label="Total Recovered", value='TotalRecovered'),
                         dict(label="New Recovered", value='NewRecovered'),
                         dict(label="Total Tests", value='TotalTests'),
                         dict(label="Tests per 1M population", value='Tests/1M pop')],
                     multi=False,
                     value="TotalCases",
                     style={"width": "60%", 'display': 'inline-block'}
                     ),
        dcc.Dropdown(id="select_k_countries",
                     options=[
                         dict(label="Top 5", value=5),
                         dict(label="Top 10", value=10),
                         dict(label="Top 25", value=25),
                         dict(label="Top 50", value=50),
                     ],
                     multi=False,
                     value=10,
                     style={"width": "30%", 'display': 'inline-block'}
                     ),

        dcc.Graph(id="k_countries_sorted", figure=init_k_countries_plot)
    ]),

    html.Div([
        html.Br(),
        html.H2("BoxPlot to explain the distribution of the variables", style={"text-align": "center"}),
        html.Br(),
        dcc.Dropdown(id="select_box_attribute",
                     options=[
                         dict(label="Deaths per 1M population", value='Deaths/1M pop'),
                         dict(label="Tests per 1M population", value='Tests/1M pop')
                     ],
                     multi=False,
                     value="Deaths/1M pop",
                     style={"width": "40%"}
                     ),

        dcc.Graph(id="continent_box_plot", figure=init_box_fig)
    ]),

    html.Div([
            html.Br(),
            html.H2("Top countries by number of Active/Critical cases.", style={"text-align": "center"}),
            html.Br(),
            dcc.Dropdown(id="select_attributes",
                         options=[
                             dict(label="Active Cases", value='ActiveCases'),
                             dict(label="Serious, Critical Cases", value='Serious,Critical')],
                         multi=False,
                         value="ActiveCases",
                         style={"width": "60%", 'display': 'inline-block'}
                         ),
            dcc.Dropdown(id="select_k_countrie",
                         options=[
                             dict(label="Top 5", value=5),
                             dict(label="Top 10", value=10),
                             dict(label="Top 25", value=25),
                         ],
                         multi=False,
                         value=10,
                         style={"width": "30%", 'display': 'inline-block'}
                         ),

            dcc.Graph(id="k_countrie_sorted", figure=init_pie_chart)
        ]),

    html.Div([
            html.Br(),
            html.H2("Geographical scatter plot", style={"text-align": "center"}),
            html.Br(),
            dcc.Dropdown(id="select_attri",
                         options=[
                             dict(label="Total Cases", value='TotalCases'),
                             dict(label="New Cases", value='NewCases'),
                             dict(label="Total Cases per 1M population", value='Tot Cases/1M pop'),
                             dict(label="Active Cases", value='ActiveCases'),
                             dict(label="Serious, Critical Cases", value='Serious,Critical'),
                             dict(label="Total Deaths", value='TotalDeaths'),
                             dict(label="New Deaths", value='NewDeaths'),
                             dict(label="Deaths per 1M population", value='Deaths/1M pop'),
                             dict(label="Total Recovered", value='TotalRecovered'),
                             dict(label="New Recovered", value='NewRecovered'),
                             dict(label="Total Tests", value='TotalTests'),
                             dict(label="Tests per 1M population", value='Tests/1M pop')],
                         multi=False,
                         value="TotalCases",
                         style={"width": "60%", 'display': 'inline-block'}
                         ),
            dcc.Graph(id="geographic_plot", figure=init_geo_plot)
            ])
    ])

# Defining the application callbacks


@app.callback(
    Output("continent_corona_bar", "figure"),
    Input("select_keyword", "value")
)
def update_continent_corona_bar(value):
    return plot_continent_data(data, keyword=value)


@app.callback(
    Output("k_countries_sorted", "figure"),
    Input("select_attribute", "value"),
    Input("select_k_countries", "value")
)
def update_k_countries_sorted(attribute, n_countries):
    return plot_top_k_countries(n_countries, attribute)


@app.callback(
    Output("continent_box_plot", "figure"),
    Input("select_box_attribute", "value")
)
def update_continent_box_plot(value):
    return plot_boxplots(data, keyword=value)


@app.callback(
    Output("k_countrie_sorted", "figure"),
    Input("select_attributes", "value"),
    Input("select_k_countrie", "value")
)
def update_pie_chart(attribute, n_countries):
    return plot_pie_chart(n_countries=n_countries, sortby=attribute)


@app.callback(
    Output("geographic_plot", "figure"),
    Input("select_attri", "value"),
)
def update_geo_plot(value):
    return geo_plot(data, keyword=value)


if __name__ == "__main__":
    countries_data = scrape_corona_data()
    data = create_clean_dataframe(countries_data)
    data = data[data.index != "Western Sahara"]  ## Removing the inexistant country called Western Sahara
    app.run_server()


