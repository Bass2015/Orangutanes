
def where_subject_and_date(df, subject, date):
    return df[(df['subject']==subject)&(df['date']==date)]