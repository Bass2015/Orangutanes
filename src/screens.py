import pandas as pd
import streamlit as st
import plotly.express as px
import yaml
from charts import Boxplot, PieChart, StackedBars, MeanBars

wr = st.write
with open('./src/config.yaml', 'r') as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)

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
                self.mean_bars()
        with st.container():
            col3, col4 = st.columns(2)
            with col3:
                self.pie_chart()
            with col4: 
                self.stacked_bars()

    def info(self):
        st.markdown(f'# {self.subject}')
        wr(CONFIG['DESC'][self.subject])

    # Deprecated
    def boxplot(self):
        behavior = st.selectbox('Behavior', CONFIG['DATASET']['macro_bhv'])
        chart = Boxplot(self.subject,
                        title=f'Time in {behavior}',
                        behavior=behavior,
                        df=self.df)
        st.plotly_chart(chart.figure(), use_container_width=True)
    
    def stacked_bars(self):
        chart = StackedBars(self.subject,
                          title='Behavior relative frequencies')
        st.plotly_chart(chart.figure(), use_container_width=True)

    def pie_chart(self):
        period = st.selectbox('Period',CONFIG['DATASET']['periods'])
        chart = PieChart(period,self.subject,
                        title="Time spent on each behavior, by period",
                        df=self.df)
        st.plotly_chart(chart.figure(),
                        use_container_width=True)

    def mean_bars(self):
        behavior = st.selectbox('Behavior', CONFIG['DATASET']['macro_bhv'])
        scatter = st.checkbox('Individual points')
        error_bar = st.checkbox('Error bar')
        chart = MeanBars(self.subject,
                        title=f'Time in {behavior}',
                        behavior=behavior,
                        error_bar=error_bar, 
                        scatter=scatter,
                        df=self.df)
        st.plotly_chart(chart.figure(), use_container_width=True)

