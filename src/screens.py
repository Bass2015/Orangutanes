import pandas as pd
import streamlit as st
import plotly.express as px
import yaml

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
                self.boxplot()
        with st.container():
            col3, col4 = st.columns(2)
            with col3:
                self.pie_chart()
            with col4: 
                self.stacked_bars()

    def info(self):
        st.markdown(f'# {self.subject}')
        wr(CONFIG['DESC'][self.subject])

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
        chart = PieChart(self.subject,
                        title="Time spent on each behavior, by period",
                        df=self.df,)
        st.plotly_chart(chart.figure(),
                        use_container_width=True)

    def update_layout(self, fig, title, lgd_title):
        fig.update_layout({'title': {
                                'text': title,
                                'x': 0.5
                            },
                           'legend': {
                                'title': lgd_title
                            },
                           'modebar': {
                                'bgcolor': 'rgba(0,0,0,0)',
                                'orientation': 'v',
                                'remove': ['autoscale', 'lasso', 'zoomin', 'zoomout', 'select']
                            },
                            'yaxis': {
                                'title': None,
                                'showgrid': False,
                                'zeroline': False
                            },
                            'xaxis': {
                                'title': None,
                                'showgrid': False,
                                'zeroline': False
                            },
                           'paper_bgcolor': 'rgba(0,0,0,0)', 
                           'plot_bgcolor': 'rgba(0,0,0,0)'
                           })

class Chart:
    def __init__(self, subject, title, df=None):
        self.subject = subject
        self.df = df
        self.title = title

    def figure(self):
        return self.fig

    def update_layout(self, title, lgd_title=None):
        self.fig.update_layout({'title': {
                                'text': title,
                                'x': 0.5
                            },
                           'legend': {
                                'title': lgd_title
                            },
                           'modebar': {
                                'bgcolor': 'rgba(0,0,0,0)',
                                'orientation': 'v',
                                'remove': ['autoscale', 'lasso', 'zoomin', 'zoomout', 'select']
                            },
                            'yaxis': {
                                'title': None,
                                'showgrid': False,
                                'zeroline': False
                            },
                            'xaxis': {
                                'title': None,
                                'showgrid': False,
                                'zeroline': False
                            },
                           'paper_bgcolor': 'rgba(0,0,0,0)', 
                           'plot_bgcolor': 'rgba(0,0,0,0)'
                           })

class PieChart(Chart):
    def __init__(self, subject, title, df=None):
        Chart.__init__(self, subject, title, df)

    def figure(self, period='pregame'):
        mask = (self.df['subject']==self.subject)&(self.df['period']==period)
        behavior_total_durations = self.df[mask] \
            .groupby('macro_bhv')['duration'] \
            .sum() \
            .reset_index()
        self.fig = px.pie(behavior_total_durations,
                     values='duration', 
                     names='macro_bhv', 
                     color='macro_bhv', 
                     color_discrete_map=CONFIG['COLORS']['behaviors'])
        self.fig.update_traces(textinfo='none')
        self.update_layout(title=self.title)
        return self.fig
    
class StackedBars(Chart):
    def __init__(self, subject, title, df=None):
        df = pd.read_csv('./data/freqs_df.csv', index_col=[0])
        Chart.__init__(self, subject, title, df)

    def figure(self):
        self.load_data()
        self.fig = px.bar(self.df,
                     x='period',
                     y='relative_freq',
                     color='macro_bhv', 
                     width=400, 
                     color_discrete_map=CONFIG['COLORS']['behaviors'])
        self.update_layout(self.title, lgd_title='Behavior')
        self.fig.update_traces(marker_line_color='rgba(0,0,0,0)')
        return self.fig

    def load_data(self):
        self.df = self.df[(self.df['subject']==self.subject)]\
                    .groupby(['period','macro_bhv'])['freq'] \
                    .sum() \
                    .reset_index()
        self.df['relative_freq'] = 0
        for period in self.df['period'].unique():
            self.calculate_rel_frequencies(period)
        periods = ['pregame', 'game', 'postgame']
        self.df['period'] = pd.Categorical(self.df['period'], categories=periods)
        self.df.sort_values(by='period', inplace=True)

    def calculate_rel_frequencies(self, period):
        sum = self.df.groupby('period')['freq'].sum()
        period_data = (self.df['period']==period).astype(int)
        rel_freqs = period_data * self.df['freq'] / sum[period]
        self.df['relative_freq'] += rel_freqs

class Boxplot(Chart):
    def __init__(self, subject, title, behavior, df=None):
        self.behavior = behavior
        Chart.__init__(self, subject, title, df)

    def figure(self):
        if not isinstance(self.subject, list):
            subjects=[self.subject]
        mask = (self.df['subject'].isin(subjects))&(self.df['macro_bhv']==self.behavior)
        df = self.df[mask]
        self.fig = px.box(df,
                          x='period',
                          y='duration',
                          color='macro_bhv', 
                          title='Individual',
                          color_discrete_map=CONFIG['COLORS']['behaviors'])
        self.update_layout(self.title, lgd_title=None)
        self.fig.update_layout({'showlegend': False, 
                                'yaxis': {'title': 'seconds'}})
        return self.fig