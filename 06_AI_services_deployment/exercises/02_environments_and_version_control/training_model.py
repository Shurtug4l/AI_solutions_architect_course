import mlflow

from sklearn.model_selection import train_test_split
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor

mlflow.sklearn.autolog()

db = load_diabetes()

X_train, X_test, y_train, y_test = train_test_split(db.data, db.target)

model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=10)

model.fit(X_train, y_train)