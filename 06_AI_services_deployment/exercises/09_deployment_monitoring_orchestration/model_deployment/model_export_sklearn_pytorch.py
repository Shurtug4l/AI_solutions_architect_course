from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import pickle

iris = load_iris()
X = iris.data
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

rf_model = RandomForestClassifier(n_estimators=100, random_state=123)

rf_model.fit(X_train, y_train)

print(rf_model.predict_proba(X_test))

path_model = 'iris_model_rf.pkl'

with open(path_model, 'wb') as file:
    pickle.dump(rf_model, file)


########
with open(path_model, 'rb') as file:
    loaded_model = pickle.load(file)

y_predict_load = loaded_model.predict_proba(X_test)
print(y_predict_load)