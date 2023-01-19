import yaml
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

with open('./src/config.yaml', 'r') as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)


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
    def __init__(self, period, subject, title, df=None):
        self.period=period
        Chart.__init__(self, subject, title, df)

    def figure(self):
        mask = (self.df['subject']==self.subject)&(self.df['period']==self.period)
        behavior_total_durations = self.df[mask] \
            .groupby('macro_bhv')['duration'] \
            .mean() \
            .reset_index()
        self.fig = px.pie(behavior_total_durations,
                     values='duration', 
                     names='macro_bhv', 
                     color='macro_bhv', 
                     color_discrete_map=CONFIG['COLORS']['behaviors'])
        self.fig.update_traces(hoverinfo='label+percent',
                textinfo='none')
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