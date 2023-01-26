import pandas as pd
import streamlit as st
import yaml
import queries
import scipy.stats as stats
from abc import ABC, abstractmethod
from dashboard.charts import Boxplot, PieChart, StackedBars, MeanBars
from data_manager import unstack_behaviors

wr = st.write
with open('./src/config.yaml', 'r') as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)

class Screen(ABC):
    def __init__(self):
        super(ABC, self).__init__()
    
    @abstractmethod
    def render(self):
        pass

class SubjectScreen(Screen):
    def __init__(self, subject):
        self.subject = subject
        self.df = pd.read_csv('./data/clean_df.csv', index_col=[0])\
                        .groupby(['date', 'reg','subject','macro_bhv', 'period'])\
                        ['duration'].sum().reset_index()
        super(SubjectScreen, self).__init__()
    
    def render(self):
        self.info()
        with st.container():
            col1, col2 = st.columns([8, 3])
            with col1:
                behavior = st.selectbox('Behavior', CONFIG['DATASET']['macro_bhv'])
                self.mean_bars(behavior)
            with col2:
                self.ttests(behavior)
        with st.container():
            col3, col4 = st.columns(2)
            with col3:
                self.pie_chart()
            with col4: 
                self.stacked_bars()

    def info(self):
        subject = 'All' if isinstance(self.subject, list) else self.subject
        st.markdown(f'# {subject}')
        wr(CONFIG['DESC'][subject])

    def ttests(self, behavior):
        df = unstack_behaviors(self.df)
        pregame_game_ttest = self.single_ttest(df, behavior, 'pregame', 'game')
        pregame_postgame_ttest = self.single_ttest(df, behavior, 'pregame', 'postgame')
        
        st.markdown(f"""The difference between **pregame** period and **game** period, 
                for {behavior} behaviors, {pregame_game_ttest[0]} significative, 
                with a p-value of {pregame_game_ttest[1]:.3f} and a significance level
                of 0.05""")
        st.markdown(f"""The difference between **pregame** period and **postgame** period, 
                for {behavior} behaviors, {pregame_postgame_ttest[0]} significative, 
                with a p-value of {pregame_postgame_ttest[1]:.3f} and a significance level
                of 0.05""")
        
    def single_ttest(self, df, behavior, periodA, periodB):
        """Returns ttest values to see if means of behavior between periodA and periodB are different"""
        A_data = queries.filter_subject_period(df, self.subject, periodA) \
                        .reset_index()[behavior]
        B_data = queries.filter_subject_period(df, self.subject, periodB) \
                        .reset_index()[behavior]
        equal_var = stats.bartlett(A_data, B_data).pvalue > 0.05
        ttest = stats.ttest_ind(A_data,B_data, equal_var=equal_var)

        significative = ttest.pvalue < 0.05
        signif_string = 'is' if significative else 'is not' 
        return signif_string, ttest.pvalue

    # Deprecated
    def boxplot(self):
        behavior = st.selectbox('Behavior', CONFIG['DATASET']['macro_bhv'])
        chart = Boxplot(self.subject,
                        title=f'Time in {behavior}',
                        behavior=behavior,
                        df=self.df)
        st.plotly_chart(chart.figure(), use_container_width=True)
    
    def stacked_bars(self):
        behaviors = st.multiselect("Behaviors: ", CONFIG['DATASET']['macro_bhv'])
        chart = StackedBars(self.subject,
                            behaviors,
                            title='Behavior relative frequencies')
        st.plotly_chart(chart.figure(), use_container_width=True)

    def pie_chart(self):
        period = st.selectbox('Period',CONFIG['DATASET']['periods'])
        chart = PieChart(period,self.subject,
                        title="Total time spent on each behavior, by period",
                        df=self.df)
        st.plotly_chart(chart.figure(),
                        use_container_width=True)

    def mean_bars(self, behavior):
        scatter = st.checkbox('Individual points')
        error_bar = st.checkbox('Error bar')
        chart = MeanBars(self.subject,
                        title=f'Mean time in {behavior}',
                        behavior=behavior,
                        error_bar=error_bar, 
                        scatter=scatter,
                        df=self.df)
        st.plotly_chart(chart.figure(), use_container_width=True)

class Methodology(Screen):
    def __init__(self):
        super(Methodology, self).__init__()

    def render(self):
        pass