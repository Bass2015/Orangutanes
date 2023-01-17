import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import yaml
from screens import SubjectDashboard

with open('./src/config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
st.set_page_config(layout='wide')
wr = st.write

def layout():
    with st.sidebar:
        subject = st.radio('Select the subject to visualize', config['DATASET']['subjects'])
    dashboard = SubjectDashboard(subject)
    dashboard.render()

layout()
