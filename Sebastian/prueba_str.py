import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx 
import graphviz as gv
from data_manager import CleanDF
from pyvis.network import Network
import streamlit.components.v1 as components
from PIL import Image


wr = st.write
# # # Titulo
# ## de qué va el estudio
st.write("# 🦧 Análisis de la terapia de juego en orangutanes")
st.write('## El estudio')
st. write('''Hipótesis: *El juego con el cuidador disminuye 
            las coductas agonísticas y mejora las conductas
            afiliativas en orangutanes*''')
#        Meter dibujito
# ## Planificación
st.write('## Planificación')
xls = pd.ExcelFile(r'./Registro orangutanes Barcelona.xlsx')
df_raw = pd.read_excel(xls,'Grupo', dtype=str)
st.write(df_raw)

st.graphviz_chart('''
    digraph {
        Raw_data -> Visualización
        Raw_data -> Grafo_social
        Raw_data -> Machine_learning
    }''')

# ## Data cleaning
wr('## Data Cleaning')
classes = Image.open('./img/classes.png')
st.image(classes)

tab1, tab2, tab3, tab4 = st.tabs(['🧼 Clean', '👀 Visualization', '📈 Graphs', '🧠 Machine Learning'])
cleandf = CleanDF(df_raw)
df = cleandf.process_df()
mldf  = pd.read_csv('./machine_learning.csv')
vis_df  = pd.read_csv('./macro_df.csv').drop('period.1', axis=1)
graph_df = pd.read_csv('./juego_graph.csv')
tab1.write(df)
tab2.write(vis_df)
tab3.write(graph_df)
tab4.write(mldf)
### Clean Dataframe
wr('''### Clean Dataframe''')

# - Mostrar clases
# ## Machine learning




pre_graph = pd.read_csv('./prejuego_graph.csv')
pre_graph.set_index('subject', inplace=True)
pre_graph *= 10
pre_graph
G = nx.from_pandas_adjacency(pre_graph)
G.name = "Graph from pandas adjacency matrix"

net = Network(notebook=True)
net.from_nx(G)
net.save_graph('prejuego.html')
HtmlFile = open(f'prejuego.html','r',encoding='utf-8')
components.html(HtmlFile.read(), height=800, width=800)


net = nn.Sequential(nn.Linear(32, 30), 
                    nn.ReLu(),
                    nn.Linear(30, 10), 
                    nn.ReLu(),
                    nn.)