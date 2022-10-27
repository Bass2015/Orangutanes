from tkinter import NE
import constants
import pandas as pd
import numpy as np
import json
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV

results = {'periods': {},
           'subjects': {}}

class NeuralNetwork(nn.Module):
    def __init__(self, input_shape, output_shape):
        super(NeuralNetwork, self).__init__()
        self.net = nn.Sequential(nn.Linear(input_shape, 20),
                                 nn.ReLU(),
                                 nn.Linear(20, 10),
                                 nn.ReLU(),
                                 nn.Linear(10, output_shape),
                                 nn.Softmax())
    
    def forward(self, x):
        return self.net.forward(x)

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
    X_train, X_test, Y_train, Y_test = train_test
    params_grid = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                     'C': [1, 10, 100, 1000]},
                    {'kernel': ['linear'], 'C': [1, 10, 100, 1000]}]
    svm_model = GridSearchCV(SVC(), params_grid, cv=5)
    svm_model.fit(X_train, Y_train.values.argmax(axis=1))
    final_model = svm_model.best_estimator_
    results[study][constants.SVM] = {}
    results[study][constants.SVM][constants.SCORE] = final_model.score(X_test, Y_test.values.argmax(axis=1))
    Y_pred = final_model.predict(X_test)
    results[study][constants.SVM][constants.CM] = confusion_matrix(Y_test.values.argmax(axis=1), Y_pred).tolist()

def neural_network(study, train_test):
    X_train, X_test, y_train, y_test = train_test
    model = NeuralNetwork(X_train.shape[1], y_train.shape[1])
    optimizer = torch.optim.Adam(model.parameters())
    num_epoch = 100
    loss_fn = nn.CrossEntropyLoss()
    data_loader = DataLoader([element for element in zip(X_train.values, y_train.values)], 32)
    for epoch in range(num_epoch):
        for input, target in data_loader:
            optimizer.zero_grad()
            output = model(input.float())
            loss = loss_fn(output.float(), target.float())
            loss.backward()
            optimizer.step()
    y_pred = model.forward(torch.tensor(X_test.values).float())
    results[study][constants.NN] = {}
    # results[study][constants.NN][constants.SCORE] = r2_score(y_test.values.argmax(), y_pred.argmax().detach().numpy())
    results[study][constants.NN][constants.CM] = confusion_matrix(y_test.values.argmax(axis=1), y_pred.argmax(axis=1)).tolist()
    

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
    # decission_tree('periods', train_test_periods)
    # decission_tree('subjects', train_test_subjects)
    # random_forest('periods', train_test_periods)
    # random_forest('subjects', train_test_subjects)
    # svm('periods', train_test_periods)
    # svm('subjects', train_test_subjects)
    neural_network('periods', train_test_periods)
    save_results()