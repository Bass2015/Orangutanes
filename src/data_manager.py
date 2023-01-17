
# Classes used to clean and process the original excel file
# Authors: Alba Avilés, Sebastián Dolgonos

from lib2to3.pgen2.pgen import DFAState
import pandas as pd
import numpy as np
import datetime as dt

xls = pd.ExcelFile(r'./Registro orangutanes Barcelona.xlsx')
df_raw = pd.read_excel(xls,'Grupo')

DATE = 'date'
SUBJECT = 'subject'
PERIOD = 'period'
REG='reg'
BEHAVIOR='behavior'
FRECUENCY='frecuency'
RECEPTOR='receptor'
DURATION='duration'

class DataManager():
    def __init__(self, df):
        self.df = df

    def process_df(self):
        return self.df
    
    def save_df(self, out_path):
        self.df.to_csv(out_path)
    
    def get_df(self):
        return self.df
    
    def to_timedelta(self,t):
        try:
            return pd.to_timedelta(str(t)).total_seconds()
        except:
            return np.nan

    def drop_columns(self, columns):
        self.df.drop(labels=columns, axis=1, inplace=True)

class CleanDF(DataManager):
    def __init__(self, df):
        super().__init__(df)

    def process_df(self):
        self.columns_to_english()
        self.clean_duration()
        self.freq_to_duration()
        self.receptor_column()
        self.behavior_to_lower()
        self.drop_columns(["Observaciones","Ubicacion","frecuency"])
        return super().process_df()
    
    def columns_to_english(self):
        columns = {'Fecha': DATE,
                   'Sujeto': SUBJECT,
                   'Periodo':PERIOD,
                   'Registro diario': REG,
                   'Conducta': BEHAVIOR,
                   'Frecuencia':FRECUENCY,
                   'Receptor': RECEPTOR,
                   'Duración': DURATION}
        self.df = self.df.rename(columns=columns)

    def receptor_column (self):
        self.df.loc[self.df[RECEPTOR] == 'Gibon*', RECEPTOR] = 'Gibon'
        self.df.loc[self.df[RECEPTOR] == 'Storma*', RECEPTOR] = 'Storma'
        self.df.loc[self.df[RECEPTOR] == 'Locky*', RECEPTOR] = 'Locky'
        self.df.loc[self.df[RECEPTOR] == 'Hadia*', RECEPTOR] = 'Hadia'
        self.df.loc[self.df[RECEPTOR] == 'Popo*', RECEPTOR] = 'Popo'
        self.df.loc[self.df[RECEPTOR] == 'Jawie*', RECEPTOR] = 'Jawie'
        self.df.loc[self.df[RECEPTOR] == 'jawie', RECEPTOR] = 'Jawie'
        
        self.df[RECEPTOR] = self.df[RECEPTOR].fillna('')
        self.df[RECEPTOR] = self.df.receptor.apply(lambda x : x.split())
        
    def clean_duration(self):
        self.df.drop(self.df[self.df[DURATION] == 'd'].index, inplace=True)
        self.df[DURATION] = self.df[DURATION].fillna(dt.time(0, 0))
        self.df[ DURATION] = np.where(self.df[DURATION].astype(str).str.fullmatch(r'\s*'),
                               dt.time(0,0),
                               self.df[DURATION])
        self.df[DURATION] = self.df[DURATION].apply(self.to_timedelta)
    
    def freq_to_duration(self):
        self.df[FRECUENCY].fillna(0, inplace=True)
        self.df[FRECUENCY] = self.df[FRECUENCY].apply(self.process_freq)
        self.df[DURATION] += self.df[FRECUENCY]
    
    def process_freq(self,x):
        if isinstance(x, str):
            x = 0
        x *= 5
        return x #pd.Timedelta(seconds=x)

    def behavior_to_lower(self):
        self.df[BEHAVIOR] = self.df[BEHAVIOR].str.lower()
 
class MLDF(DataManager):
    def __init__(self, df):
        super().__init__(df)

    def process_df(self):
        self.conduct_to_columns()
        self.one_hot(PERIOD)
        self.one_hot(SUBJECT)
        self.drop_columns([REG, DATE, PERIOD, SUBJECT])
        return super().process_df()

    def conduct_to_columns(self):
        self.df = self.df.groupby([PERIOD, DATE, REG, SUBJECT, BEHAVIOR])[DURATION] \
            .sum() \
            .unstack(BEHAVIOR) \
            .fillna(0) \
            .reset_index()
        self.df.columns.name =''

    def one_hot(self, column):
        self.df = pd.concat([self.df, pd.get_dummies(self.df[column])], axis=1)

class GraphDF(DataManager):
    def __init__(self, df):
        super().__init__(df)

    def process_df(self):
        self.keep_subject_receptor()
        self.drop_empties_receptor()
        self.unpack_todos()
        self.process_receptor_column()
        self.prejuego_g, self.juego_g, self.postjuego_g = self.create_periods_graphs()
        print(self.graphs)
        return super().process_df()
    
    def keep_subject_receptor(self):
        self.df.loc[:,[SUBJECT,RECEPTOR]]

    def drop_empties_receptor(self):
        empties = self.df[RECEPTOR].apply(lambda x : len(x)==0)
        index_to_drop = self.df[list(empties)].index
        self.df.drop(index_to_drop, inplace=True)

    def unpack_todos(self):
        todos_mask = self.df[RECEPTOR].apply(lambda x : x[0] == 'Todos')
        print(todos_mask.sum())
        todos_index =self.df[todos_mask].index[0]
        subjects = list(self.df.subject.unique())
        self.df.at[todos_index, RECEPTOR] = subjects
    
    def process_receptor_column(self):
        self.df.explode(RECEPTOR)
        self.df.loc[self.df[RECEPTOR] == 'Hadia*', RECEPTOR] = 'Hadia'
        self.df.loc[self.df[RECEPTOR] == 'Jawie*', RECEPTOR] = 'Jawie'
        self.df.loc[self.df[RECEPTOR] == 'locky', RECEPTOR] = 'Locky'
    
    def create_periods_graphs(self):
        self.df[PERIOD] = self.df[PERIOD].str.lower()
        a = self.create_graph('prejuego')
        b = self.create_graph('juego')
        c = self.create_graph('postjuego')
        return a, b, c
    
    def create_graph(self, period):
        df = self.df[self.df[PERIOD] == period]
        graph = df.groupby(SUBJECT)[RECEPTOR] \
                  .value_counts() \
                  .unstack(RECEPTOR) \
                  .fillna(0) \
                  .astype(int)
        return graph


xls = pd.ExcelFile(r'./Registro orangutanes Barcelona.xlsx')
df_raw = pd.read_excel(xls,'Grupo')
cleandf = CleanDF(df_raw)
mldf = MLDF(cleandf.process_df())
mldf.process_df()
mldf.save_df('machine_learning.csv')
