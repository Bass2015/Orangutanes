import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx 
from data_manager import CleanDF
from pyvis.network import Network
import streamlit.components.v1 as components


xls = pd.ExcelFile(r'./Registro orangutanes Barcelona.xlsx')
df_raw = pd.read_excel(xls,'Grupo')
cleandf = CleanDF(df_raw)

df = cleandf.process_df()
df
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
