import pandas as pd
import numpy as np
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import dcc,html
from dash.dependencies import Input,Output
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template

# Data loading and cleaning

def load_data():
    df = pd.read_csv('./assets/nobel_prize_corrected.csv')
    #Creating an age column 
    df['dateAwarded'] = pd.to_datetime(df['dateAwarded'])
    df['birth_date'] = pd.to_datetime(df['birth_date'])
    df['age'] = (df['dateAwarded'].dt.year - df['birth_date'].dt.year)
    #Renaming the gender column
    df['gender'] = df['gender'].map({'male':'Male','female':'Female'})
    return df

df = load_data()

#Load bootstrap css
dbc_css = "https://www.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
load_figure_template("SLATE")

# Create app

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SLATE,dbc_css])
server = app.server



# Desing app layout

app.layout = dbc.Container(
    children=[
        dbc.Row([
            dbc.Col([
                html.H1("Nobel Prize Dashboard",
                        style={'textAlign':'center','display':'flex','align-items':'center','justify-content':'center'})
            ],className='dbc'),
            html.P("Select a category: ",style={'textAlign':'center','display':'flex','align-items':'center','justify-content':'center'})
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card(dcc.Dropdown(
                    id='category-dropdown',
                    options=[
                        {'label':'Economic Sciences','value':'Economic Sciences'},
                        {'label':'Physics','value':'Physics'},
                        {'label':'Chemistry','value':'Chemistry'},
                        {'label':'Peace','value':'Peace'},
                        {'label':'Physiology or Medicine','value':'Physiology or Medicine'},
                        {'label':'Literature','value':'Literature'},
                    ],
                    value='Economic Sciences', 
                    className='dbc',
                    style={'textAlign':'center','align-items':'center','justify-content':'center','fontColor':'black'}           
                ))
            ],width=4)       
        ],style={'textAlign':'center','align-items':'center','justify-content':'center','paddingBottom':10}),
        
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(id='world-map')),width=4),
            dbc.Col(dbc.Card(dcc.Graph(id='country-bar')),width=4),
            dbc.Col(dbc.Card(dcc.Graph(id='affiliation-bar')),width=4),    
        ]),
        
        dbc.Row([    
            dbc.Col(dbc.Card(dcc.Graph(id='gender-pie')),width=4), 
            dbc.Col(dbc.Card(dcc.Graph(id='age-hist')),width=4),  
            dbc.Col(dbc.Card(dcc.Graph(id='migration-pie')),width=4)
            
        ])     
],style={'padding': 10}, fluid=True,className='dbc')


@app.callback(
    [Output('world-map','figure'),Output('country-bar','figure'),Output('affiliation-bar','figure'),Output('gender-pie','figure'),Output('migration-pie','figure'),Output('age-hist','figure')],
    Input('category-dropdown','value')
)

def update_map(selected_category):
    if not selected_category:
        raise PreventUpdate
    
    #Filtering by the selected category
    
    df_cat = df.query("category == @selected_category")
    
    #Calculating data for choropleth map
    countries = df_cat.groupby('birth_countryNow')['birth_countryNow'].count().reset_index(name = 'count')
    
    #Calculating data for gender pie chart
    gender = df_cat.groupby('gender')['gender'].count().reset_index(name = 'count')
    
    #Calculating data for affiliations bar chart
    df_affiliations = pd.concat([df_cat['affiliation_1'], df_cat['affiliation_2'],df_cat['affiliation_3'],df_cat['affiliation_4']])
    df_affiliations = df_affiliations.str.split(',', expand=True)[0].to_frame(name='affiliation')
    affiliation = df_affiliations['affiliation'].value_counts().reset_index()

    #Calculating data for inmigration pie chart
    df_cat['mig_status'] = np.where(df_cat['birth_country'] == df_cat['death_country'],"Native","Inmigrant")
    mig_country = df_cat.groupby("mig_status")['mig_status'].count().reset_index(name = 'count')
    
    #World Map
    
    fig1 = px.choropleth(
        countries,
        locations ="birth_countryNow",
        color = "count",
        locationmode = 'country names',
        color_continuous_scale =px.colors.sequential.Peach_r,
        title = f"Geographical distribution for {selected_category} "      
    ).update_layout(
        margin={"r":0,"t":100,"l":0,"b":100},
        title_x=0.5,
        hoverlabel = {
            'bgcolor':'white',
            'font_size': 15,
            'font_family': 'Arial'
        },
        coloraxis_showscale=False).update_geos(
            fitbounds="locations",
            visible=True)
    
    #Countries Bar Chart
    fig2 = px.bar(
        countries.sort_values(by='count',ascending=False)[:10],
        x='birth_countryNow',
        y='count',
        color= 'birth_countryNow',
        color_discrete_sequence=px.colors.qualitative.G10,
        title = f"Top 10 countries for {selected_category}",
    ).update_layout(
        title_x=0.5,
        bargap = 0.1,
        xaxis_title = "Country",
        yaxis_title = "Count",
        showlegend=False,
        hoverlabel = {
            'bgcolor':'white',
            'font_size': 15,
            'font_family': 'Arial'
        }
    )
    
    #Affiliations Bar Chart
    fig3 = px.bar(
        affiliation[0:10],
        y='affiliation',
        x = 'count',
        color = 'affiliation',
        color_discrete_sequence=px.colors.qualitative.G10,
        title=f"Top 10 affiliations for {selected_category}"
    ).update_xaxes(tickangle=60).update_layout(
        title_x=0.5,
        bargap = 0.1,
        xaxis_title = "Count",
        yaxis_title = "Affiliation",
        showlegend=False,
        hoverlabel = {
            'bgcolor':'white',
            'font_size': 15,
            'font_family': 'Arial'
        }
    )
    
    #Gender Bar Chart
    fig4 = px.pie(
        gender,
        names='gender',
        values ='count',
        color_discrete_sequence=px.colors.qualitative.G10,
        title=f"Gender distribution for {selected_category}"
    ).update_traces(textposition='outside', textinfo='percent+label').update_layout(
        showlegend = False,
        title_x=0.5,
        hoverlabel = {
            'bgcolor':'white',
            'font_size': 15,
            'font_family': 'Arial'
        }
    )
    
    #Inmigration Bar Chart
    fig5 = px.pie(
        mig_country,
        names='mig_status',
        values ='count',
        color_discrete_sequence=px.colors.qualitative.G10,
        title=f"Inmigration distribution for {selected_category}"
    ).update_traces(textposition='inside', textinfo='percent+label').update_layout(
        showlegend = False,
        title_x=0.5,
        hoverlabel = {
            'bgcolor':'white',
            'font_size': 15,
            'font_family': 'Arial'
        }
    )
    
    #Age Histogram
    fig6 = px.histogram(
        df_cat,
        x='age',
        histnorm = 'probability',
        marginal = 'box', 
        color_discrete_sequence=px.colors.qualitative.G10,
        title=f"Age distribution for {selected_category}"
    ).update_layout(
        title_x=0.5,
        bargap = 0.1,
        xaxis_title = "Age",
        yaxis_title = "Probability",
        hoverlabel = {
            'bgcolor':'white',
            'font_size': 12,
            'font_family': 'Arial'
        }
    )
    

    return fig1,fig2,fig3,fig4,fig5,fig6
    



if __name__=='__main__':
    app.run_server(debug=True) 