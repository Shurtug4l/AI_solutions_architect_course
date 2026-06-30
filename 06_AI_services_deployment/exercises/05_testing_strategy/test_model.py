from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np

def train_model(X, y):
    model = LinearRegression()
    model.fit(X, y)
    return model

def make_predictions(model, X):
    return model.predict(X)

def test__model():
    # Dati di esempio (input X e output y)
    X = np.array([[1], [2], [3], [4], [5]])
    y = np.array([2, 4, 6, 8, 10])

    model = train_model(X, y)

    predictions = make_predictions(model, X)

    # Verifica che l'errore quadratico medio sia molto basso (quasi zero)
    mse = mean_squared_error(y, predictions)
    assert mse < 1e-6, f"Mean squared error troppo alto: {mse}"
