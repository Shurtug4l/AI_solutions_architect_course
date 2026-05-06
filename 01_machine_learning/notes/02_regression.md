# Regression

## Problem Formulation

Regression predicts a **continuous** output $y$ from input features $\mathbf{x}$. The goal is to learn a function $f$ such that $\hat{y} = f(\mathbf{x}) \approx y$.

---

## Linear Regression

Models the relationship as a linear combination of features:

$$\hat{y} = w_0 + w_1 x_1 + w_2 x_2 + \ldots + w_n x_n = \mathbf{w}^T \mathbf{x} + b$$

where $\mathbf{w}$ are weights (coefficients) and $b$ is the bias (intercept).

### Loss Function: Mean Squared Error

$$\mathcal{L} = \frac{1}{m} \sum_{i=1}^{m} (y_i - \hat{y}_i)^2$$

MSE penalizes large errors quadratically, making it sensitive to outliers. This is the quantity minimized during training.

### Normal Equation (closed-form solution)

$$\mathbf{w}^* = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$$

- Exact solution, no iterations needed
- Requires $\mathbf{X}^T \mathbf{X}$ to be invertible (fails if features are perfectly collinear)
- Computationally expensive: $O(n^3)$ due to matrix inversion — impractical for $n > 10^4$ features

---

## Gradient Descent

Iterative optimization used when the normal equation is too slow or the problem is not closed-form.

$$\mathbf{w} \leftarrow \mathbf{w} - \eta \nabla_{\mathbf{w}} \mathcal{L}$$

where $\eta$ is the **learning rate**.

### Variants

| Variant | Gradient computed on | Pros | Cons |
|---------|---------------------|------|------|
| **Batch GD** | Entire training set | Stable convergence | Slow per step on large data |
| **Stochastic GD (SGD)** | 1 sample | Fast updates, escapes local minima | Noisy, unstable convergence |
| **Mini-batch GD** | Batch of 32–512 | Balance of speed and stability | Most commonly used in practice |

**Learning rate selection**: too high → divergence; too low → slow convergence. Use learning rate schedules or adaptive optimizers (Adam) to reduce manual tuning.

---

## Polynomial Regression

Extends linear regression to capture non-linear relationships by adding polynomial terms:

$$\hat{y} = w_0 + w_1 x + w_2 x^2 + w_3 x^3 + \ldots$$

This is still **linear in the parameters** — the model remains a linear regression applied to transformed features. Use `PolynomialFeatures` in sklearn to generate the expanded feature matrix.

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

poly_pipe = Pipeline([
    ('poly', PolynomialFeatures(degree=3, include_bias=False)),
    ('lr',   LinearRegression())
])
```

Higher degree → more expressive but more prone to overfitting. Always pair with regularization or cross-validated model selection.

---

## Regression Metrics

### Mean Absolute Error (MAE)

$$\text{MAE} = \frac{1}{m} \sum |y_i - \hat{y}_i|$$

- Robust to outliers (linear penalty)
- Interpretable in the same units as $y$

### Mean Squared Error (MSE) / Root MSE (RMSE)

$$\text{MSE} = \frac{1}{m} \sum (y_i - \hat{y}_i)^2 \qquad \text{RMSE} = \sqrt{\text{MSE}}$$

- RMSE is in the same units as $y$
- Penalizes large errors more than MAE
- The training objective for linear regression

### R² (Coefficient of Determination)

$$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

- Measures the proportion of variance in $y$ explained by the model
- $R^2 = 1$: perfect fit; $R^2 = 0$: model is no better than predicting the mean; $R^2 < 0$: worse than the mean
- Adding features always weakly increases $R^2$ even if they are noise — use **adjusted $R^2$** to penalize extra parameters

### Adjusted R²

$$R^2_{\text{adj}} = 1 - (1 - R^2) \cdot \frac{m - 1}{m - n - 1}$$

where $m$ = samples, $n$ = features. Penalizes model complexity; use when comparing models with different numbers of features.

---

## Assumptions of Linear Regression

Violations do not make the model fail outright, but they affect the reliability of inference (confidence intervals, p-values):

| Assumption | What to check | Fix if violated |
|-----------|--------------|-----------------|
| **Linearity** | Residual vs fitted plot (should be random) | Add polynomial terms, transform features |
| **Homoscedasticity** | Residual variance constant across fitted values | Log-transform target, robust regression |
| **Independence** | Residuals uncorrelated | Relevant for time series; use ARIMA/sequential models |
| **Normality of residuals** | Q-Q plot | Not required for large samples (CLT); required for small-sample inference |
| **No perfect multicollinearity** | VIF > 10 signals a problem | Drop features, use Ridge regression |

---

## Multicollinearity

When features are highly correlated, coefficient estimates become unstable (high variance). The model still predicts well but coefficients are not individually interpretable.

**Variance Inflation Factor (VIF)**:

$$\text{VIF}_j = \frac{1}{1 - R^2_j}$$

where $R^2_j$ is the R² from regressing feature $j$ on all other features. VIF > 5–10 indicates problematic collinearity.

Fixes: remove one of the correlated features, use PCA, or apply Ridge regression (L2 regularization shrinks correlated coefficients together).

---

## Quick Reference

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae  = mean_absolute_error(y_test, y_pred)
r2   = r2_score(y_test, y_pred)

print(model.coef_)       # weights
print(model.intercept_)  # bias
```
