import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import yaml
from dashboard.screens import SubjectScreen, StatisticsScreen

with open('./src/config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

st.set_page_config(layout='wide')
wr = st.write

def layout():
    with st.sidebar:
        selection = st.selectbox('Options:', ['Individual dashboards', 'Statistics'])
        if selection == 'Individual dashboards':
            subject_list = config['DATASET']['subjects']
            subject_list.append('All')
            subject = st.radio('Select the subject to visualize', subject_list)
    if selection == 'Individual dashboards':
        if subject == 'All':
            subject = config['DATASET']['subjects']
        dashboard = SubjectScreen(subject)
        dashboard.render()
    if selection == 'Statistics':
        dashboard = StatisticsScreen()
        dashboard.render()
        

if __name__ == '__main__':
    layout()
