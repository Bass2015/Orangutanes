import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
# # import networkx as nx 
import plotly.express as px
# # import json
# # import constants
import numpy as np
# # from data_manager import CleanDF
# # from pyvis.network import Network
# from PIL import Image

wr = st.write
SUBJECTS =['Karl', 'Hadia', 'Popo', 'Locky', 'Storma', 'Jawie']


def layout():
    with st.sidebar:
        subject = st.radio('Select the subject to visualize', SUBJECTS)
    dashboard = SubjectDashboard(subject)
    dashboard.render()

def calculate_rel_frequencies(x, period):
    sum = x.groupby('period')['freq'].sum()
    x['relative_freq'] += (x['period']==period).astype(int)*x['freq'] / sum[period]

class SubjectDashboard:
    def __init__(self, subject):
        self.subject = subject
        self.df = pd.read_csv('./data/clean_df.csv', index_col=[0])\
                        .groupby(['date', 'reg','subject','macro_bhv', 'period'])\
                        ['duration'].sum().reset_index()
    
    def render(self):
        with st.container():
            col1, col2 = st.columns([3, 8])
            with col1:
                self.info()
            with col2:
                self.boxplot()
        with st.container():
            col3, col4 = st.columns(2)
            with col3:
                self.pie_chart()
            with col4: 
                self.stacked_bars()

    
    def info(self):
        st.markdown(f'# {self.subject}')
        wr('''Lorem ipsum dolor si amet, consectetur 
        adipiscing incidunt ut labore et dolore magna aliquam
         erat nostrud exercitation ullamcorper suscipit laboris
          nis duis autem vel eum irure dolor in reprehenderit i,
           dolore eu fugiat nulla pariatur. At vero eos et accusa
            praesant luptatum delenit aigue duos dolor et mole
             provident, simil tempor sunt in culpa qui officia de
              fuga. Et harumd dereud facilis est er expedit disti 
              eligend optio congue nihil impedit doming id quod 
              assumenda est, omnis dolor repellend.''')

    def boxplot(self):
        if not isinstance(self.subject, list):
            subjects=[self.subject]
        df = self.df[(self.df['subject'].isin(subjects))&(self.df['macro_bhv']=='Individual')]
        fig = px.box(df, x='period', y='duration', color='period', width=500, title='Individual')
        st.plotly_chart(fig, use_container_width=True)
    
    def stacked_bars(self):
        freq = pd.read_csv('./data/freqs_df.csv', index_col=[0])
        freq = freq[(freq['subject']==self.subject)]\
                    .groupby(['period','macro_bhv'])['freq'] \
                    .sum() \
                    .reset_index()
        freq['relative_freq'] = 0
        calculate_rel_frequencies(freq,'pregame')
        calculate_rel_frequencies(freq,'game')
        calculate_rel_frequencies(freq,'postgame')
        st.plotly_chart(px.bar(freq,
                               x='period',
                               y='relative_freq',
                               color='macro_bhv', 
                               width=400),
                        use_container_width=True)

    def pie_chart(self):
        mask = (self.df['subject']==self.subject)&(self.df['period']=='postgame')
        behavior_total_durations = self.df[mask] \
            .groupby('macro_bhv')['duration'] \
            .sum() \
            .reset_index()
        st.plotly_chart(px.pie(behavior_total_durations,
                               values='duration', 
                               names='macro_bhv'),
                        use_container_width=False)


layout()
