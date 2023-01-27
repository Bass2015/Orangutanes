import pandas as pd
import scipy.stats as stats
import queries
from data_manager import unstack_behaviors

def ind_diff_between_periods(df, periodA, periodB) -> pd.DataFrame:
    """Returns DF with p-values for each individual and behavior, between periodA and periodB"""
    unstacked = unstack_behaviors(df)
    unstacked.sort_values(by='subject', inplace=True)
    results = {}
    for sub in unstacked.subject.unique():
        for bhv in df['macro_bhv'].unique():
            test = single_ttest(sub, unstacked, bhv, periodA, periodB)[1]
            results[bhv] = results.get(bhv, [])
            results[bhv].append(test)
    return pd.DataFrame(results, index=unstacked.subject.unique())
    
    
          
def single_ttest(subject, df, behavior, periodA, periodB):
    """Returns ttest p- values to see if means of behavior between periodA 
    and periodB are different"""
    A_data = queries.filter_subject_period(df, subject, periodA) \
                    .reset_index()[behavior]
    B_data = queries.filter_subject_period(df, subject, periodB) \
                    .reset_index()[behavior]
    if len(A_data) < 30:
        pd.concat([A_data, pd.Series(0, index=[30])])
    if len(B_data) < 30:
        pd.concat([B_data, pd.Series(0, index=[30])])
    equal_var = stats.bartlett(A_data, B_data).pvalue > 0.05
    ttest = stats.ttest_ind(A_data,B_data, equal_var=equal_var)

    significative = ttest.pvalue < 0.05
    signif_string = 'is' if significative else 'is not' 
    return  signif_string, ttest.pvalue