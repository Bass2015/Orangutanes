import constants
import pandas as pd
import numpy as np
import json
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder

results = {'periods': {},
           'subjects': {}}

def decission_tree(study, train_test):
    X_train, X_test, y_train, y_test = train_test
    seed = 13640121
    model = DecisionTreeClassifier(criterion='gini', random_state=seed)
    model.fit(X_train, y_train)
    results[study][constants.DT] = {}
    results[study][constants.DT][constants.SCORE] = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    results[study][constants.DT][constants.CM] = confusion_matrix(y_test.values.argmax(axis=1), y_pred.argmax(axis=1)).tolist()

def random_forest(study, train_test):
    X_train, X_test, y_train, y_test = train_test
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    results[study][constants.RF] = {}
    results[study][constants.RF][constants.SCORE] = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    results[study][constants.RF][constants.CM] = confusion_matrix(y_test.values.argmax(axis=1), y_pred.argmax(axis=1)).tolist()

def svm(study, train_test):
    X_train, X_test, y_train, y_test = train_test
    params_grid = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
    # Transforming non numerical labels into numerical labels

    encoder = LabelEncoder()

    # encoding train labels 
    encoder.fit(y_train.columns)
    Y_train = encoder.transform(y_train.columns)

    # encoding test labels 
    encoder.fit(y_test.columns)
    Y_test = encoder.transform(y_test.columns)
    
    # Performing CV to tune parameters for best SVM fit 

    svm_model = GridSearchCV(SVC(), params_grid, cv=5)
    svm_model.fit(X_train, Y_train)
    final_model = svm_model.best_estimator_
    results[study][constants.SVM] = {}
    results[study][constants.SVM][constants.SCORE] = final_model.score(X_test, Y_test)
    Y_pred = final_model.predict(X_test)
    results[study][constants.SVM][constants.CM] = confusion_matrix(Y_test.values.argmax(axis=1), Y_pred.argmax(axis=1)).tolist()

def train_test(keep, drop, mldf):
    df = mldf.drop(drop, axis=1)
    data = df.drop(keep, axis=1)
    data = data.divide(data.sum(axis=1), axis=0)
    target = df[keep]
    return train_test_split(data, target, test_size=constants.SPLIT_RATIO)

def save_results():
    with open('results.json', 'w') as f:
        json.dump(results, f)

if __name__ == '__main__':
    mldf = pd.read_csv('./machine_learning.csv')
    mldf.drop('Unnamed: 0', axis=1, inplace=True)
    train_test_periods = train_test(constants.PERIODS, constants.SUBJECTS, mldf)
    train_test_subjects = train_test(constants.SUBJECTS, constants.PERIODS, mldf)
    decission_tree('periods', train_test_periods)
    decission_tree('subjects', train_test_subjects)
    random_forest('periods', train_test_periods)
    random_forest('subjects', train_test_subjects)
    # svm('periods', train_test_periods)
    # svm('subjects', train_test_subjects)
    save_results()