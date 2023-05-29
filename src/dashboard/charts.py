import yaml
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from abc import ABC, abstractmethod

with open('./src/config.yaml', 'r') as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)


class Chart(ABC):
    def __init__(self, subject, title, df=None):
        if not isinstance(subject, list):
            self.subject=[subject]
        else: 
            self.subject = subject
        self.df = df
        self.title = title
        super(Chart, self).__init__()

    @abstractmethod
    def figure(self):
        return self.fig

    def sort_periods(self):
        periods = ['pregame', 'game', 'postgame']
        self.df['period'] = pd.Categorical(self.df['period'], categories=periods)
        self.df.sort_values(by='period', inplace=True)
    
    def unstack_behaviors(self):
        self.df = self.df.groupby(['period', 'date','subject', 'reg','macro_bhv'])\
                         ['duration'] \
                         .sum() \
                         .unstack(level='macro_bhv', fill_value=0) \
                         .reset_index()

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
        super(PieChart, self).__init__(subject, title, df)

    def figure(self):
        mask = (self.df['subject'].isin(self.subject))&(self.df['period']==self.period)
        behavior_total_durations = self.df[mask] \
            .groupby('macro_bhv')['duration'] \
            .sum() \
            .reset_index()
        self.fig = px.pie(behavior_total_durations,
                     values='duration', 
                     names='macro_bhv', 
                     color='macro_bhv', 
                     color_discrete_map=CONFIG['COLORS']['behaviors'])
        self.fig.update_traces(hoverinfo='label+percent',
                textinfo='none', 
                hovertemplate="Behavior: %{label} <br> Mean time: %{percent}")
        self.update_layout(title=self.title)
        return self.fig
    
class StackedBars(Chart):
    def __init__(self, subject, behaviors, title, df=None):
        self.behaviors = behaviors
        df = pd.read_csv('./data/freqs_df.csv', index_col=[0])
        super(StackedBars, self).__init__(subject, title, df)

    def figure(self):
        self.load_data()
        self.df = self.df[self.df['macro_bhv'].isin(self.behaviors)]
        self.fig = px.bar(self.df,
                     x='period',
                     y='relative_freq',
                     color='macro_bhv', 
                     width=400, 
                     category_orders={'period':['pregame', 'game', 'postgame']},
                     color_discrete_map=CONFIG['COLORS']['behaviors'])
        self.update_layout(self.title, lgd_title='Behavior')
        self.fig.update_traces(marker_line_color='rgba(0,0,0,0)', 
                               hovertemplate="""Period: %{x} <br> 
                                                Frequency: %{y:.2f}
                                            """)
        return self.fig

    def load_data(self):
        self.df = self.df[(self.df['subject'].isin(self.subject))]\
                    .groupby(['period','macro_bhv'])['freq'] \
                    .sum() \
                    .reset_index()
        self.df['relative_freq'] = 0
        for period in self.df['period'].unique():
            self.calculate_rel_frequencies(period)
        self.sort_periods()
        

    def calculate_rel_frequencies(self, period):
        sum = self.df.groupby('period')['freq'].sum()
        period_data = (self.df['period']==period).astype(int)
        rel_freqs = period_data * self.df['freq'] / sum[period]
        self.df['relative_freq'] += rel_freqs

class Boxplot(Chart):
    def __init__(self, subject, title, behavior, df=None):
        self.behavior = behavior
        super(Boxplot, self).__init__(subject, title, df)
        self.unstack_behaviors()

    def figure(self):
        
        mask = (self.df['subject'].isin(self.subject))
        df = self.df[mask]
        self.fig = px.box(df,
                          x='period',
                          y=self.behavior,
                          category_orders={'period':['pregame', 'game', 'postgame']},
                         )
        self.update_layout(self.title, lgd_title=None)
        self.fig.update_layout({'showlegend': False, 
                                'yaxis': {'title': 'seconds'}})
        return self.fig
    
class MeanBars(Chart):
    def __init__(self, subject, title, behavior, error_bar, scatter, df=None):
        self.behavior = behavior
        self.error_bar = error_bar
        self.scatter = scatter
        super(MeanBars, self).__init__(subject, title, df)
        self.unstack_behaviors()
    
    def figure(self):
        self.df = self.df[self.df['subject'].isin(self.subject)]
        statistics = self.behavior_means_stds()
        self.fig = px.bar(x=CONFIG['DATASET']['periods'],
                y=statistics['means']/60)

        self.beautify(statistics)
        return self.fig

    def beautify(self, statistics):
        self.update_layout(self.title, lgd_title=None)
        self.fig.update_traces(marker_color=CONFIG['COLORS']['behaviors'][self.behavior],
                               marker_line_color='rgba(0,0,0,0)', 
                               hovertemplate="Period: %{x} <br> Mean time: %{y:.2f} min")
        self.plot_points_and_error(statistics)

    def plot_points_and_error(self, statistics):
        color = CONFIG['COLORS']['bhv_highlight'][self.behavior]
        if self.error_bar:
            self.fig.update_traces(error_y=dict(type='data',
                              array=statistics['stds'], 
                              color=color))
        if self.scatter:                
            self.fig.add_trace(go.Scatter(
                            x=self.df.period, 
                            y=self.df[self.behavior], 
                            mode='markers',
                            marker={'color':color}, 
                            name='', 
                            hovertemplate="Ind. point: %{y:.2f}")
                         )
        
    def behavior_means_stds(self):
        return pd.DataFrame({
            'means': [self.get_stat('mean', 'pregame'),
                      self.get_stat('mean', 'game'),
                      self.get_stat('mean', 'postgame')],
            'stds': [self.get_stat('std', 'pregame'),
                      self.get_stat('std', 'game'),
                      self.get_stat('std', 'postgame')]
                      })

    def get_stat(self, stat, period):
        return self.df.query(f"period=='{period}'") \
                .describe() \
                .loc[stat, self.behavior]