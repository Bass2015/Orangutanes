from lib2to3.pgen2.pgen import DFAState
import pandas as pd

DATE = 'date'
SUBJECT = 'subject'

class DataManager():
    def __init__(self, df):
        self.df = df

    def process_df(self):
        return self.df

class CleanDF(DataManager):
    def __init__(self, df):
        super(CleanDF, self).__init__(df)

    def process_df(self):
        self.drop_columns()
        self.columns_to_english()
        self.freq_to_duration()
        super().process_df()
    
    def columns_to_english(self):
        columns = {'Fecha': DATE,
                   'Sujeto': SUBJECT,
                   'Periodo':'period',
                   'Registro diario': 'reg',
                   'Conducta': 'behavior',
                   'Frecuencia':'frencuency',
                   'Receptor': 'receptor',
                   'Duración': 'duration'}
        self.df = self.df.rename(columns=columns)

    def freq_to_duration(self):
        pass
    
    def drop_columns(self):
        self.df = self.df.drop(labels=["Observaciones","Ubicacion"], axis=1)



dm = CleanDF(pd.DataFrame([1,2]))
dm.process_df()

