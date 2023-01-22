
def filter_subject_and_date(df, subject, date):
    return df[(df['subject']==subject)&(df['date']==date)]

def filter_subject_period_bhv(df, subject, period, behavior):
    subject_mask = df['subject'] == subject
    period_mask = df['period'] == period
    behavior_mask = df['macro_bhv'] == behavior
    mask = subject_mask & period_mask & behavior_mask
    return df[mask]

def filter_subject_period(df, subject, period):
    subject_mask = df['subject'] == subject
    period_mask = df['period'] == period
    mask = subject_mask & period_mask
    return df[mask]