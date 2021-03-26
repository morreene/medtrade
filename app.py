import pandas as pd
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

mapbox_access_token = 'pk.eyJ1IjoibW9ycmVlbmUiLCJhIjoiY2s5Mmg4azdlMDdkaTNvbXNmYzNqM3V1YyJ9.7DJTX_x8ucJAndaOP-Q49g'
eu_members = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France',
              'Germany', 'Greece','Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands',
              'Poland', 'Portugal', 'Romania', 'Slovak Republic', 'Slovenia', 'Spain', 'Sweden',
              # 'United Kingdom'
              ]
data = pd.read_csv('med_trade_test20210325.csv')
# data = data[data['type']=='tariff']
# print(data.shape)
# migration_years = [2019]

country_list = data[data['region'] != 'Aggregates']['country'].unique()
data_countries = (data[data['country'].isin(country_list) &
                       ~data['country'].isin(['Latin America & Caribbean','Sub-Saharan Africa'])].reset_index(drop=True))

product_translation = {
    'all':        'All medical products',
    'medicines':  'Medicines',
    'supplies':   'Medical supplies',
    'equipment':  'Medical equipment',
    'protective': 'Personal protective products'
}

indicator_translation = {
    'tariff_applied':   'MFN applied tariff',
    'tariff_bound':     'Bound tariff',
    'tariff_bcoverage': 'Binding coverage',
    'tariff_rta':       'Preferential tariff in RTAs',
    'export2019':           'Export value (2019)',
    'import2019':           'Import value (2019)',
    'export2020':           'Export value (2020 1st half)',
    'import2020':           'Import value (2020 1st half)',
}

bar_buttons = [
    "zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d",
    # "resetScale2d",
    "hoverClosestCartesian", "hoverCompareCartesian",
    "zoom3d", "pan3d",
    # "resetCameraDefault3d",
    # "resetCameraLastSave3d",
    "hoverClosest3d",
    "orbitRotation", "tableRotation",
    "zoomInGeo", "zoomOutGeo", "resetGeo", "hoverClosestGeo",
    # "toImage",
    "sendDataToCloud",
    "hoverClosestGl2d",
    "hoverClosestPie",
    "toggleHover",
    # "resetViews",
    "toggleSpikelines",
    "resetViewMapbox"
]

all_countries_regions = data['country'].unique()

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
# external JavaScript files
# <!-- Global site tag (gtag.js) - Google Analytics -->
# <script async src="https://www.googletagmanager.com/gtag/js?id=UA-62289743-7"></script>
# <script>
#   window.dataLayer = window.dataLayer || [];
#   function gtag(){dataLayer.push(arguments);}
#   gtag('js', new Date());
#
#   gtag('config', 'UA-62289743-7');
# </script>


# external_scripts = [
#     'https://www.googletagmanager.com/gtag/js?id=UA-62289743-7',
# ]
external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.7/css/bootstrap.min.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                # external_scripts=external_scripts
                )
app.title = 'Trade in Medical Goods'


app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-62289743-7"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'UA-62289743-7');
        </script>




        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""








server = app.server

app.layout = html.Div([
    dbc.Row([
        # html.Br(),
        dbc.Col(lg=1),
        dbc.Col([
            html.Br(),
            html.Div(
                id="header",
                children=[
                    html.H2(children="Trade in Medical Goods", style={'color': 'black', 'font-weight': 'bold'}),
                    html.P(
                        id="description",
                        children=dcc.Markdown(
                          children=(
                            '''
                            This site provides graphical representations of tariffs and trade data used in the information notes on [1) Trade in Medical Goods in the Context of Tackling COVID-19](https://www.wto.org/english/news_e/news20_e/rese_03apr20_e.pdf),
                            [2) its update with Developments in the First Half of 2020](https://www.wto.org/english/tratop_e/covid19_e/medical_goods_update_e.pdf) and [3) Treatment of Medical Products in Regional Trade Agreements (RTAs)](https://www.wto.org/english/tratop_e/covid19_e/medical_products_report_e.pdf).
                            The study is an overview of the trade of medical goods ([the list of products](https://www.wto.org/english/tratop_e/covid19_e/medical_good_annexes_e.xlsx)),
                            including bound, MFN applied and preferential tariffs on these products.
                            It should be noted that this study focuses solely on the final form of these products and does not extend to the different intermediate products that are used by global value chains in their production.
                            The import and export values are calculated at the level of HS 6-digit subheadings, which, to a certain extent, could cover products that are not for medical use. ''')
                        )
                    ),
                ],
            ),
        ], lg=9),
    ]),

    dbc.Row([
        html.Br(),
        dbc.Col(lg=1),
        dbc.Col([
            html.Br(),
            dbc.Label('Select an indicator:'),
            dcc.Dropdown(id='indicator_dropdown_top',
                         placeholder='Select an indicator',
                         value='tariff_applied',
                         clearable=False,
                         options=[{'label': v, 'value': k}
                                  for k, v in indicator_translation.items()])
        ], lg=2),

        dbc.Col([
            html.Br(),
            dbc.Label('Select a product group:'),
            dcc.Dropdown(id='metrics_dropdown_top',
                         placeholder='Select a product group',
                         value='all',
                         clearable=False,
                         options=[{'label': v, 'value': k}
                                  for k, v in product_translation.items()])
        ], lg=2),


        # dbc.Col([
        #     html.Br(),
        #     dbc.Label('Select a year:'),
        #     dcc.Slider(id='year_slider',
        #                tooltip={'always_visible': True},
        #                min=min(migration_years),
        #                max=max(migration_years),
        #                value=2019,
        #                included=False,
        #                step=None,
        #                marks={year: {'label': str(year)}
        #                       for year in migration_years})
        # ], lg=2),
    ]),
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            dbc.Row([
                    dcc.Graph(id='world_map',
                              config={'displayModeBar': 'hover',
                                      'displaylogo': False,
                                      'showTips': True,
                                      'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'hoverClosestGeo'],
                                      'toImageButtonOptions': {'format': 'png'}}),

                ]),
           html.P(style={'textAlign': 'right', 'margin': 'auto', 'marginBottomTop': '15%'},
                  children=['Data is not available for countries or territories in white color.']),
           # html.Br(),

        ], lg=7),
        dbc.Col([
            dcc.Graph(id='top_countries',
                      config={
                              # 'displayModeBar': True,
                              'displayModeBar': 'hover',
                              'displaylogo': False,
                              'showTips': True,
                              'modeBarButtonsToRemove': bar_buttons,
                              'toImageButtonOptions': {'format': 'png'}
                             })
        ], lg=3)
    ]),

    dbc.Row([
        dbc.Col([], lg=1),
        dbc.Col([
            dbc.Label('Select an indicator:'),
            dcc.Dropdown(id='indicator_dropdown_bottom',
                         placeholder='Select an indicator',
                         value='tariff_applied',
                         clearable=False,
                         options=[{'label': v, 'value': k}
                                  for k, v in indicator_translation.items()])
        ], lg=2),

        dbc.Col([
            dbc.Label('Select a product group:'),
            dcc.Dropdown(id='metrics_dropdown_bottom',
                         placeholder='Select a product group',
                         value='all',
                         clearable=False,
                         options=[{'label': v, 'value': k}
                                  for k, v in product_translation.items()])
        ], lg=2),

        dbc.Col([
            dbc.Label('Select members:'),
            dcc.Dropdown(id='countries_regions_dropdown',
                         multi=True,
                         value=['Argentina','Brazil','Chad', 'China', 'Kazakhstan', 'United States of America' ],
                         placeholder='Select members',
                         options=[{'label': country, 'value': country}
                                  for country in all_countries_regions])
        ], lg=6),
    ]),

    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            dcc.Graph(id='metric_bars',
            # config={'displayModeBar': False},
              config={
                      # 'displayModeBar': True,
                      'displayModeBar': 'hover',
                      'displaylogo': False,
                      'showTips': True,
                      'modeBarButtonsToRemove': bar_buttons,
                      'toImageButtonOptions': {'format': 'png'}
                     }
            )
        ], lg=10)
    ]),

    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
                    html.Br(),
                    html.P(
                        id="description11",
                        style={'font-size': 11},
                        children=dcc.Markdown(
                          children=(
                            '''
                            Note: _The United Kingdom has communicated that as a member State of the European Union until 31 January 2020, the instrument of acceptance of the
                            European Union for the Information Technology Agreement also covers participation by the United Kingdom whilst it was a member State of the European Union,
                            and will continue to do so during the transition period afforded under Withdrawal Agreement.
                            See document [WT/GC/206](https://docs.wto.org/dol2fe/Pages/SS/directdoc.aspx?filename=q:/WT/GC/206.pdf) and the EU note verbale
                            ([WT/LET/1462](https://docs.wto.org/dol2fe/Pages/SS/directdoc.aspx?filename=q:/WT/LET/1462.pdf)) for more information._
                            ''')
                        )
                    ),
                    html.Br(),html.Br(),
                    html.Div(
                      id='my-footer',
                      style={'marginLeft': '1.5%', 'marginRight': '1.5%', 'marginBottom': '1%', 'marginTop': '.5%'},
                             children=[
                                 html.Hr(style={'marginBottom': '.5%'},),
                                 html.P(style={'textAlign': 'center', 'margin': 'auto'},
                                        children=[
                                                  html.A('Download raw data', href='https://timeseries.wto.org/', target='_blank'), ' | ',
                                                  html.A('Tariff Analysis Online', href='https://tao.wto.org',target='_blank'), " | ",
                                                  html.A('About WTO', href='https://www.wto.org/english/thewto_e/thewto_e.htm', target='_blank'), ' | ',
                                                  html.A('Disclaimer', href='https://www.wto.org/english/info_e/disclaimer_e.htm', target='_blank'), ' | ',
                                                  html.A('Contact: idb@wto.org', href="mailto:idb@wto.org", target='_blank')
                                        ]
                                  ),
                                   html.P(style={'textAlign': 'center', 'margin': 'auto', 'marginTop': '.5%'},
                                          children=['Last updated on 26 March 2021']
                                    ),
                              ]
                          ),
        ], lg=10)
    ])
], style={'backgroundColor': '#eeeeee'})

# Bottom bar chart
@app.callback(Output('metric_bars', 'figure'),
              [Input('countries_regions_dropdown', 'value'),
               Input('indicator_dropdown_bottom', 'value'),
               Input('metrics_dropdown_bottom', 'value')])
def plot_country_timeseries(countries, indicator, metric):
    if not countries or not metric:
        raise PreventUpdate
    fig = go.Figure()
    for country in countries:
        df = data[(data['country'] == country) & (data['type'] == indicator)].drop_duplicates(subset=[metric])

        # to change conditional to indicator
        if indicator.startswith('tariff'):
            df[metric] = [format(x, '.1%') for x in df[metric]]
            fig.layout.yaxis.ticksuffix = '%'
        else:
            df[metric] = [format(int(n), ',') for n in df[metric]]
            # fig.layout.yaxis.ticksuffix = 'million USD'

            # hover_metric_str = (df[metric].mul(100).round(2).astype(str)
            #                     if indicator.startswith('tariff') else
            #                     df[metric] = [format(int(n/1000000), ',') for n in df[metric]])

        # fig.add_scatter(x=df['year'], y=df[metric], name=country,
        #                 hoverlabel={'namelength': 200},
        #                 mode='markers+lines')
        hover_suffix = ''
        # hover_metric_str = (df[metric].mul(100).round(2).astype(str)
        #                     if indicator.startswith('tariff') else
        #                     [format(int(n/1000000), ',') for n in df[metric]])

        fig.add_bar(x=df['country'], y=df[metric],
                        showlegend=False,
                        # name=country,
                        hoverlabel={'namelength': 200},
                        # mode='markers+lines'
                        hovertemplate=('<b>' + df[metric].astype(str) + '</b>' + "<extra></extra>"),
                        # hover_suffix = hover_suffix
                        )

    fig.layout.template = 'none'
    fig.layout.paper_bgcolor = '#eeeeee'
    fig.layout.plot_bgcolor = '#eeeeee'
    fig.layout.title = ('<b>' + indicator_translation[indicator] + ': '+ product_translation[metric] +
                        '</b><br>' + ', '.join(countries) + ' '# +
                        # df['year'].min().astype(str) + ' - ' +
                        # df['year'].max().astype(str)
                        )
    return fig.to_dict()

# Top country bar chart
@app.callback(Output('top_countries', 'figure'),
              [Input('indicator_dropdown_top', 'value'),
               Input('metrics_dropdown_top', 'value')])
def plot_top_countries(indicator, metric):
    if not metric:
        raise PreventUpdate
    df = (data_countries[data_countries[metric].notna()]
          .query('type == @indicator')
          .query('country != "World"')
          .sort_values(metric))

    if indicator.startswith('tariff'):
        df[metric] = df[metric].mul(100).round(1)
        df_plot = df.head(10).append(df.tail(10))
        title_begin = 'Top and Bottom 10 Members<br>'
    else:
        df_plot = df.tail(20)
        title_begin = 'Top 20 Members<br>'

    fig = go.Figure()
    fig.add_bar(x=df_plot[metric],
                y=df_plot['country'],
                orientation='h',
                marker={'color': ['rgba(186,228,174, 1)']*10 +
                                 ['rgba(129,190,162, 1)']*10
                        if indicator.startswith('tariff') else 'rgba(129,190,162, 1)'}
                )
    fig.layout.title = (title_begin + indicator_translation[indicator] + ':<br>' +
                        product_translation[metric] + '<br><br>')

    if indicator.startswith('tariff'):
        fig.layout.xaxis.ticksuffix = '%'
    fig.layout.template = 'none'
    fig.layout.margin = {'l': 150}
    fig.layout.height = 600
    fig.layout.yaxis.showgrid = True
    fig.layout.paper_bgcolor = '#eeeeee'
    fig.layout.plot_bgcolor = '#eeeeee'
    return fig.to_dict()


# # Geo map
# @app.callback(Output('world_map', 'figure'),
#               [Input('indicator_dropdown_top', 'value'),
#                Input('metrics_dropdown_top', 'value')])
# def plot_world_map(indicator, metric):
#     if not metric:
#         raise PreventUpdate
#
#     df = data_countries[data_countries[metric].notna()].sort_values(metric).query('type == @indicator')
#     # print(df.head())
#     # print(indicator)
#     # print(metric)
#     # zeroidx = df[metric].sort_values().lt(0).sum()
#     df.loc[df['country'].isin(eu_members),'country'] = 'European Union'
#     fig = go.Figure()
#     hover_suffix = ('%' if indicator.startswith('tariff') else ' million USD')
#     # hover_indicator = ('%' if indicator == 'tariff' else '')
#     hover_metric_str = (df[metric].mul(100).round(2).astype(str)
#                         if indicator.startswith('tariff') else
#                         [format(int(n/1000000), ',') for n in df[metric]])
#     fig.add_choropleth(locations=df['iso3c'],
#                        z=df[metric].clip(1, 100000000000) if not indicator.startswith('tariff') else df[metric],
#                        # z= df[metric],
#                        name='',
#                        # colorscale='cividis',
#                        colorscale = 'Reds',
#                        hoverlabel={'namelength': 200, 'bgcolorsrc': 'blah'},
#                        hovertemplate=('<b>' + df['country'] + '</b><br><br>' +
#                                       indicator_translation[indicator] + '<br>' +
#                                       product_translation[metric] + ': ' +
#                                       hover_metric_str + hover_suffix),
#                        colorbar={'lenmode': 'fraction', 'len': 0.5, 'x': -0.07,
#                                  'ticksuffix': '+' if not indicator.startswith('tariff') else '',
#                                  'tickformat': '%' if indicator.startswith('tariff') else '',
#                                  'showticksuffix': 'last' if metric == 'medicines' else 'all' },
#                        locationmode='ISO-3')
#     fig.layout.geo = {
#         'showframe': False,
#         'oceancolor': '#eeeeee',
#         'bgcolor': '#eeeeee',
#         'showocean': True,
#         'lataxis': {'range': [-51, 83]},
#     }
#     fig.layout.height = 550
#     fig.layout.margin = {'r': 10, 'l': 10, 't': 90}
#     fig.layout.margin.autoexpand = True
#     fig.layout.paper_bgcolor = '#eeeeee'
#     fig.layout.plot_bgcolor = '#eeeeee'
#     fig.layout.title = {'text': indicator_translation[indicator] + ': ' +  product_translation[metric],
#                         'font': {'color': 'black'},
#                         'x': 0.5, 'y': 0.90,
#                         'xanchor': 'center', 'yanchor': 'middle'
#                         }
#     return fig.to_dict()


## Top geomap by Mapbox
from urllib.request import urlopen
import json
with open('worldnew3.geo.json') as response:
    geocounties = json.load(response)

@app.callback(Output('world_map', 'figure'),
              [Input('indicator_dropdown_top', 'value'),
               Input('metrics_dropdown_top', 'value')])
def plot_world_map(indicator, metric):
    if not metric:
        raise PreventUpdate

    df = data_countries[data_countries[metric].notna()].sort_values(metric).query('type == @indicator')
    df = df.rename(columns={'iso3c':'iso_a3'})
    df = df[df['country']!='World']
    max_clip = df[metric].max()
    max_clip -= max_clip % -1000000000
    # print(max_clip)

    if indicator.startswith('tariff'):
        df.loc[df['country'].isin(eu_members),'country'] = 'European Union'

    if indicator == 'import2019':
        zeroidx=df[metric].clip(1, max_clip)
    elif indicator == 'export2019':
        zeroidx=df[metric].clip(1, max_clip)
    else:
        zeroidx=df[metric]

    # print(df.head())
    # print(indicator)
    # print(metric)
    # zeroidx = df[metric].sort_values().lt(0).sum()
    # fig = go.Figure()

    hover_suffix = ('%' if indicator.startswith('tariff') else ' million USD')
    # hover_indicator = ('%' if indicator == 'tariff' else '')
    hover_metric_str = (df[metric].mul(100).round(2).astype(str)
                        if indicator.startswith('tariff') else
                        [format(int(n/1000000), ',') for n in df[metric]])

    # print(df['iso_a3'].head())
    # print(df[metric].head(100))


    import numpy as np
    fig = go.Figure(go.Choroplethmapbox(geojson=geocounties,
                                        locations=df['iso_a3'],

                                        # z=df[metric].clip(1, 200000000000) if not indicator.startswith('tariff') else df[metric],
                                        # z=np.log10(zeroidx),

                                        z=zeroidx,

                                        # colorscale="Viridis_r",
                                        colorscale="algae",

                                        # zmin=0, zmax=1,
                                        marker_opacity=0.5,
                                        marker_line_width=0,
                                        # hoverlabel={'namelength': 200, 'bgcolorsrc': 'blah'},
                                        hovertemplate=('<b>' + df['country'] + '</b><br><br>' +
                                                      indicator_translation[indicator] + '<br>' +
                                                      product_translation[metric] + ': ' +
                                                      hover_metric_str + hover_suffix + "<extra></extra>"),
                                        colorbar={'lenmode': 'fraction', 'len': 0.5, 'x': -0.07,
                                                 # 'ticksuffix': '+' if not indicator.startswith('tariff') else '',
                                                 'tickformat': '%' if indicator.startswith('tariff') else '',
                                                 'showticksuffix': 'last' if metric == 'medicines' else 'all',
                                                 'yanchor':'top',
                                                 'thickness': 10,
                                                 # for log scale color
                                                 # 'tickvals': [ np.log10(100000), np.log10(1000000), np.log10(10000000), np.log10(100000000)],
                                                 # 'ticktext': [ '1M', '1B', '100B', '200B'],
                                                 },
                                        )
                    )

    fig.update_layout(
                        mapbox_style="carto-positron",
                      mapbox_zoom=0.5,
                      # mapbox_center = {"lat": 37.0902, "lon": -95.7129}
                      mapbox_center = {"lat": 30.0902, "lon": 9.7129},

        # mapbox=go.layout.Mapbox(
        #     accesstoken=mapbox_access_token,
        #     # style="light",
        #     style = 'mapbox://styles/morreene/ck9eefm732eu81ir0ke5lj422',
        #     # The direction you're facing, measured clockwise as an angle from true north on a compass
        #     bearing=0,
        #     # center=go.layout.mapbox.Center(
        #     #     lat=latitude,
        #     #     lon=longitude
        #     # ),
        #     pitch=0,
        #     # zoom=zoom
        # )




                      )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.layout.height = 550
    fig.layout.margin = {'r': 10, 'l': 10, 't': 70, 'b': 10}
    fig.layout.paper_bgcolor = '#eeeeee'
    fig.layout.plot_bgcolor = '#eeeeee'
    fig.layout.title = {'text': indicator_translation[indicator] + ': ' +  product_translation[metric],
                        'font': {'color': 'black'},
                        'x': 0.5, 'y': 0.93,
                        'xanchor': 'center', 'yanchor': 'middle'
                        }

    return fig.to_dict()

if __name__ == '__main__':
    app.run_server(debug=True)
