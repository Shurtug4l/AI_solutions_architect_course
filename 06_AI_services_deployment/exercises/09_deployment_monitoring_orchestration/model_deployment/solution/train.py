from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np

import pickle

wine = load_wine()
X = wine.data
y = wine.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# save the data in local
np.savetxt("X_test.csv", X_test, delimiter=",", fmt='%d')
np.savetxt("y_test.csv", y_test, delimiter=",", fmt='%d')

rf_model = RandomForestClassifier(n_estimators=100, random_state=123)

rf_model.fit(X_train, y_train)

path_model = 'wine_model_rf.pkl'

with open(path_model, 'wb') as file:
    pickle.dump(rf_model, file)
