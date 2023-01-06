import streamlit as st
import pandas as pd
import networkx as nx 
import plotly.express as px
import json
import constants
import numpy as np
from data_manager import CleanDF
from pyvis.network import Network
import streamlit.components.v1 as components
from PIL import Image


wr = st.write

# ---------------Titulo-----------------------
# ## de qué va el estudio
st.write("# 🦧 Análisis de la terapia de juego en orangutanes")
st.write('## El estudio')
st. write('''Hipótesis: *El juego con el cuidador disminuye 
            las coductas agonísticas y mejora las conductas
            afiliativas en orangutanes*''')
gorilas = Image.open('./img/gorilas.png')
st.image(gorilas)
#        Meter dibujito

# -------------- Planificación --------------------
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

#----------------- Data cleaning -----------------------
wr('## Data Cleaning')
classes = Image.open('./img/classes.png')
st.image(classes)

tab1, tab2, tab3, tab4 = st.tabs(['🧼 Clean', '👀 Visualization', '📈 Graphs', '🧠 Machine Learning'])
cleandf = CleanDF(df_raw)
df = cleandf.process_df()
mldf  = pd.read_csv('./machine_learning.csv')
macro_df  = pd.read_csv('./macro_df.csv').drop('period.1', axis=1)
graph_df = pd.read_csv('./juego_graph.csv')
tab1.write(df)
tab2.write(macro_df)
tab3.write(graph_df)
tab4.write(mldf)
# --------------- Visualización ---------------------
wr('## Visualización')
df_fq = pd.read_csv('./df_fq.csv').set_index('Unnamed: 0', drop=True)
# df_fq.iloc[:,1:] = df_fq.iloc[:,1:].astype(float).divide(df_fq.sum(), axis=1)
df_fq = df_fq.divide(df_fq.sum(), axis=1)
fig_fre = px.histogram(macro_df, x="period", y=[df_fq['fq_relativa_ago'],
                                               df_fq['fq_relativa_afi']],
                       barmode='group',color_discrete_sequence=px.colors.qualitative.Pastel)
fig_fre.update_layout(
    title="Relative Frecuency",
    xaxis_title="period",
    yaxis_title="relative frequency",
    legend_title="behaviors")
    
fig_fre.for_each_trace(lambda t: t.update(name = {"wide_variable_0": "agonisticas", "wide_variable_1": "afiliativas"}[t.name]))
df_fq
st.plotly_chart(fig_fre)

macro_df
# macro_df = macro_df.divide(macro_df.sum(), axis=1)
fig = px.histogram(macro_df, x="period", y=['duracion_agonisticas', 'duracion_publico', 'duracion_afiliativas',
       'duracion_ludico_social', 'duracion_sexual', 'duracion_ludicas'], barmode='group',color_discrete_sequence=px.colors.qualitative.Pastel,category_orders={"period": ["Prejuego","Juego","Postjuego"]})
fig.update_layout(
    title="Duration",
    xaxis_title="period",
    yaxis_title="% duration",
    legend_title="behaviors")
fig
# -------------- Grafos -------------------

wr('## Social Graphs')
tab1, tab2, tab3 = st.tabs(['Prejuego', 'Juego', 'Postjuego'])

pre_graph = pd.read_csv('./prejuego_graph.csv')
pre_graph.set_index('subject', inplace=True)
pre_graph *= 10
G = nx.from_pandas_adjacency(pre_graph)
G.name = "Grafo social, periodo prejuego"

net = Network(notebook=True)
net.from_nx(G)
net.save_graph('prejuego.html')
HtmlFile = open(f'prejuego.html','r',encoding='utf-8')

with tab1: 
    components.html(HtmlFile.read(), height=800, width=800)

juego_graph = pd.read_csv('./juego_graph.csv')
juego_graph.set_index('subject', inplace=True)
juego_graph *= 10
G = nx.from_pandas_adjacency(juego_graph)
G.name = "Grafo social, periodo prejuego"

net = Network(notebook=True)
net.from_nx(G)
net.save_graph('juego.html')
HtmlFile = open(f'juego.html','r',encoding='utf-8')

with tab2: 
    components.html(HtmlFile.read(), height=800, width=800)

post_juego_graph = pd.read_csv('./postjuego_graph.csv')
post_juego_graph.set_index('subject', inplace=True)
post_juego_graph *= 10
G = nx.from_pandas_adjacency(post_juego_graph)
G.name = "Grafo social, periodo prejuego"

net = Network(notebook=True)
net.from_nx(G)
net.save_graph('post_juego.html')
HtmlFile = open(f'post_juego.html','r',encoding='utf-8')

with tab3: 
    components.html(HtmlFile.read(), height=800, width=800)

# -------------- Machine learning -------------------

wr('## Machine Learning')
wr('### Periods')
tab1, tab2, tab3, tab4 = st.tabs(['Decission Trees', 'Random Forest', 'SVM', 'Neural Network'])

with open('results.json', 'r') as f:
    results = json.load(f)

# DECISSION--------
score = results['periods'][constants.DT][constants.SCORE]
cm = results['periods'][constants.DT][constants.CM]
cm = cm / np.asarray(cm).astype(np.float).sum(axis=1)

tab1.write(f'__Score__: {score}')
tab1.plotly_chart(px.imshow(cm,
          title='Decission tree model confusion matrix',
          labels=dict(x='Predicted', y='Truth', color='Percentage'),
          x=['Prejuego', 'Juego', 'Postjuego'],
          y=['Prejuego', 'Juego', 'Postjuego']))

# RANDOM FOREST--------
score = results['periods'][constants.RF][constants.SCORE]
cm = results['periods'][constants.RF][constants.CM]
cm = cm / np.asarray(cm).astype(np.float).sum(axis=1)


tab2.write(f'__Score__: {score}')
tab2.plotly_chart(px.imshow(cm,
          title='Decission tree model confusion matrix',
          labels=dict(x='Predicted', y='Truth', color='Percentage'),
          x=['Prejuego', 'Juego', 'Postjuego'],
          y=['Prejuego', 'Juego', 'Postjuego']))

# SVM -----------
score = results['periods'][constants.SVM][constants.SCORE]
cm = results['periods'][constants.SVM][constants.CM]
cm = cm / np.asarray(cm).astype(np.float).sum(axis=1)


tab3.write(f'__Score__: {score}')
tab3.plotly_chart(px.imshow(cm,
          title='Decission tree model confusion matrix',
          labels=dict(x='Predicted', y='Truth', color='Percentage'),
          x=['Prejuego', 'Juego', 'Postjuego'],
          y=['Prejuego', 'Juego', 'Postjuego']))

# NEURAL ------
score = results['periods'][constants.NN][constants.SCORE]
cm = results['periods'][constants.NN][constants.CM]
cm = cm / np.asarray(cm).astype(np.float).sum(axis=1)

tab4.write(f'__Score__: {score}')
tab4.plotly_chart(px.imshow(cm,
          title='Decission tree model confusion matrix',
          labels=dict(x='Predicted', y='Truth', color='Percentage'),
          x=['Prejuego', 'Juego', 'Postjuego'],
          y=['Prejuego', 'Juego', 'Postjuego']))

# SUBJECTS  ------------

wr('### Subjects')
tab1, tab2, tab3, tab4 = st.tabs(['Decission Trees', 'Random Forest', 'SVM', 'Neural Network'])

with open('results.json', 'r') as f:
    results = json.load(f)

# DECISSION--------
score = results['subjects'][constants.DT][constants.SCORE]
cm = results['subjects'][constants.DT][constants.CM]
cm = cm / np.asarray(cm).astype(np.float).sum(axis=1)

tab1.write(f'__Score__: {score}')
tab1.plotly_chart(px.imshow(cm,
          title='Decission tree model confusion matrix',
          labels=dict(x='Predicted', y='Truth', color='Percentage'),
          x=['Karl', 'Locky', 'Jawie', 'Storma', 'Popo', 'Hadia'],
          y=['Karl', 'Locky', 'Jawie', 'Storma', 'Popo', 'Hadia']))

# RANDOM FOREST--------
score = results['subjects'][constants.RF][constants.SCORE]
cm = results['subjects'][constants.RF][constants.CM]
cm = cm / np.asarray(cm).astype(np.float).sum(axis=1)


tab2.write(f'__Score__: {score}')
tab2.plotly_chart(px.imshow(cm,
          title='Decission tree model confusion matrix',
          labels=dict(x='Predicted', y='Truth', color='Percentage'),
          x=['Karl', 'Locky', 'Jawie', 'Storma', 'Popo', 'Hadia'],
          y=['Karl', 'Locky', 'Jawie', 'Storma', 'Popo', 'Hadia']))

# SVM -----------
score = results['subjects'][constants.SVM][constants.SCORE]
cm = results['subjects'][constants.SVM][constants.CM]
cm = cm / np.asarray(cm).astype(np.float).sum(axis=1)


tab3.write(f'__Score__: {score}')
tab3.plotly_chart(px.imshow(cm,
          title='Decission tree model confusion matrix',
          labels=dict(x='Predicted', y='Truth', color='Percentage'),
          x=['Karl', 'Locky', 'Jawie', 'Storma', 'Popo', 'Hadia'],
          y=['Karl', 'Locky', 'Jawie', 'Storma', 'Popo', 'Hadia']))

# NEURAL ------
score = results['subjects'][constants.NN][constants.SCORE]
cm = results['subjects'][constants.NN][constants.CM]
cm = cm / np.asarray(cm).astype(np.float).sum(axis=1)

tab4.write(f'__Score__: {score}')
tab4.plotly_chart(px.imshow(cm,
          title='Decission tree model confusion matrix',
          labels=dict(x='Predicted', y='Truth', color='Percentage'),
          x=['Karl', 'Locky', 'Jawie', 'Storma', 'Popo', 'Hadia'],
          y=['Karl', 'Locky', 'Jawie', 'Storma', 'Popo', 'Hadia']))

# ------------