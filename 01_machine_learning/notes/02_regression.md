# Regression

## TL;DR

Regression predicts a **continuous** output from input features. The classical workhorse is **linear regression**, which models $\hat{y}$ as a weighted combination of features and a bias. The training loss is **MSE** (mean squared error), which has a closed-form solution (the **normal equation**) for small problems but is solved by **gradient descent** for anything large or non-linear. Polynomial features extend the model to non-linear relationships while keeping it linear in the parameters — beware overfitting at high degrees. Five metrics matter: **MAE** (robust, same units as $y$), **MSE / RMSE** (penalises large errors more, RMSE is the training objective), **R²** (variance explained, can mislead by always growing with more features), and **adjusted R²** (penalised for the number of features). The classical assumptions of linear regression — linearity, homoscedasticity, independence, normality of residuals, no perfect multicollinearity — affect inference (confidence intervals, p-values), not predictive accuracy: the model still fits, it just becomes harder to make statistical claims about the coefficients. Multicollinearity destabilises coefficients (high VIF); the fix is to drop redundant features or apply Ridge regularisation (covered in 03).

## Cheatsheet

| Concept | Formula / sklearn | Note |
|---|---|---|
| Linear model | `LinearRegression()` — `ŷ = wᵀx + b` | Closed form via normal equation |
| Loss | MSE = `(1/m) Σ(yᵢ − ŷᵢ)²` | Convex, differentiable |
| Closed-form | `w* = (XᵀX)⁻¹ Xᵀy` | Exact; O(n³) inversion, n = features |
| Gradient descent | `w ← w − η ∇L` | When closed form is too costly |
| Polynomial | `PolynomialFeatures(degree=3)` + `LinearRegression()` | Linear in parameters |
| MAE | `mean_absolute_error` | Robust, same units as y |
| MSE / RMSE | `mean_squared_error` | RMSE = sqrt; same units as y |
| R² | `r2_score` | Variance explained; can be < 0 |
| Adjusted R² | manual: `1 - (1 - R²)(m-1)/(m-n-1)` | Penalises extra features |
| Multicollinearity | `VIF_j = 1 / (1 - R²_j)` | > 5-10 = problem |
| Fix multicollinearity | Drop feature, PCA, or Ridge | Last is the most common fix |

---

## Problem formulation

Regression learns a function $f$ such that $\hat{y} = f(\mathbf{x}) \approx y$ for a continuous target. The simplest functional form is linear; everything more sophisticated (polynomial, regularised, generalised additive models, neural networks) builds on the same loss-and-optimiser pattern.

---

## Linear regression

Models the relationship as a linear combination of features:

$$\hat{y} = w_0 + w_1 x_1 + w_2 x_2 + \ldots + w_n x_n = \mathbf{w}^T \mathbf{x} + b$$

where $\mathbf{w}$ are the **weights** (coefficients) and $b$ is the **bias** (intercept). Each $w_j$ has a clean interpretation: the change in $\hat{y}$ for a one-unit change in $x_j$, holding all other features fixed.

### Loss: mean squared error

$$\mathcal{L} = \frac{1}{m} \sum_{i=1}^{m} (y_i - \hat{y}_i)^2$$

MSE penalises large errors quadratically — a single big miss contributes more than many small misses combined. This makes MSE sensitive to outliers but produces a smooth, convex loss with a unique minimum, which is exactly what you want for fast, deterministic optimisation.

### Normal equation (closed-form solution)

$$\mathbf{w}^* = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$$

The exact minimum of the MSE loss, no iterations. Three caveats:

- $\mathbf{X}^T \mathbf{X}$ must be invertible; it isn't if features are perfectly collinear.
- The matrix inversion is $O(n^3)$ in the number of features, which becomes impractical above ~10⁴ features.
- Numerical stability degrades on near-collinear features; in practice, sklearn uses a more stable least-squares solver (SVD-based) rather than literally inverting the matrix.

For most real-world problems, the closed form is the default; switch to gradient descent only when the data is too large or the model isn't linear in the parameters.

---

## Gradient descent

Iterative optimisation. Useful when the closed form is too slow or the loss isn't differentiable in closed form.

$$\mathbf{w} \leftarrow \mathbf{w} - \eta \, \nabla_{\mathbf{w}} \mathcal{L}$$

$\eta$ is the **learning rate** — too small and convergence crawls; too large and the iterates oscillate or diverge.

### Variants

| Variant | Gradient computed on | Pros | Cons |
|---|---|---|---|
| **Batch GD** | Entire training set | Stable convergence | Slow per step on large data |
| **Stochastic GD (SGD)** | One sample | Fast updates, escapes shallow minima | Noisy convergence path |
| **Mini-batch GD** | Batch of 32-512 | Balance of speed and stability | The default in practice |

**Adaptive optimisers** (Adam, AdamW, RMSProp) adjust the learning rate per parameter based on gradient history. They're the default for neural networks and reduce the burden of manually tuning $\eta$. For linear regression itself, the closed form is almost always preferable.

---

## Polynomial regression

Extends linear regression to capture non-linear relationships by adding polynomial terms:

$$\hat{y} = w_0 + w_1 x + w_2 x^2 + w_3 x^3 + \ldots$$

Crucially, this is still **linear in the parameters** $w_j$ — the model is a linear regression applied to transformed features. `PolynomialFeatures` in sklearn generates the expanded feature matrix:

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

poly_pipe = Pipeline([
    ('poly', PolynomialFeatures(degree=3, include_bias=False)),
    ('lr',   LinearRegression()),
])
```

Higher degree → more expressive but more prone to overfitting. The number of features grows polynomially with degree (degree 3 on $n$ features creates $\binom{n+3}{3}$ terms), so practical degrees are usually 2 or 3. Always pair high-degree polynomial features with regularisation (Ridge, Lasso, Elastic Net) and select the degree via cross-validation.

---

## Regression metrics

### Mean absolute error (MAE)

$$\text{MAE} = \frac{1}{m} \sum_{i=1}^{m} |y_i - \hat{y}_i|$$

- Robust to outliers (linear penalty).
- Interpretable in the same units as $y$ — "the model is off by an average of $X$ units".

### Mean squared error / root MSE

$$\text{MSE} = \frac{1}{m} \sum_{i=1}^{m} (y_i - \hat{y}_i)^2 \qquad \text{RMSE} = \sqrt{\text{MSE}}$$

- RMSE is in the same units as $y$, MSE in squared units.
- Penalises large errors more than MAE — a single 10-off prediction is treated as 100× worse than a 1-off.
- The training objective for linear regression. Reporting RMSE alongside MAE makes the outlier sensitivity visible.

### R² (coefficient of determination)

$$R^2 = 1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$$

- Measures the proportion of variance in $y$ explained by the model.
- $R^2 = 1$ is a perfect fit; $R^2 = 0$ means the model is no better than predicting $\bar{y}$; $R^2 < 0$ means worse than the mean baseline.
- Adding features always weakly increases $R^2$, even if the new features are pure noise. Use **adjusted R²** (below) when comparing models with different numbers of features.

### Adjusted R²

$$R^2_{\text{adj}} = 1 - (1 - R^2) \cdot \frac{m - 1}{m - n - 1}$$

where $m$ = samples, $n$ = features. Penalises model complexity: adding an irrelevant feature lowers adjusted R² even though plain R² would rise. Use when comparing models with different feature counts on the same data.

---

## Assumptions of linear regression

Violations don't make the model fail outright — predictions can still be good. They affect the reliability of **statistical inference** (confidence intervals, p-values for individual coefficients, hypothesis tests):

| Assumption | What to check | Fix if violated |
|---|---|---|
| **Linearity** | Residual vs fitted plot should look like random scatter, no pattern | Add polynomial terms, transform features (log, sqrt) |
| **Homoscedasticity** | Residual variance constant across fitted values | Log-transform target, robust regression, GLS |
| **Independence** | Residuals uncorrelated | Relevant for time series; use ARIMA / sequential models |
| **Normality of residuals** | Q-Q plot | Not strictly required for large samples (CLT applies); matters for small-sample inference |
| **No perfect multicollinearity** | VIF > 10 indicates a problem | Drop a feature, use Ridge |

If you only care about prediction (not interpretation of individual coefficients), most assumption violations matter less than the choice of regularisation and feature engineering.

---

## Multicollinearity

When features are highly correlated, coefficient estimates become **unstable** — small changes in the data produce large changes in coefficients. The model still predicts well, but the coefficients are not individually interpretable: you can't tell which of two correlated features "really" causes the effect, because they're sharing weight in arbitrary proportions.

### Variance inflation factor (VIF)

$$\text{VIF}_j = \frac{1}{1 - R^2_j}$$

where $R^2_j$ is the R² from regressing feature $j$ on all other features. Rule of thumb: VIF > 5-10 indicates problematic collinearity.

### Fixes

- **Drop one of the correlated features** (the simplest, often the right answer).
- **PCA / dimensionality reduction** — replaces correlated features with orthogonal principal components.
- **Ridge regression** (L2 regularisation) — shrinks correlated coefficients together, stabilising the estimates without dropping features. See [03_bias_variance_and_regularization.md](03_bias_variance_and_regularization.md).

---

## Quick reference

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

print(model.coef_)              # weights
print(model.intercept_)         # bias
```

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Forgetting to scale features for regularised regression | Penalty applied unevenly | Always scale before Ridge / Lasso (and inside a `Pipeline`) |
| Polynomial degree too high | R² near 1 on train, terrible on test | Cross-validate degree; pair with regularisation |
| Reporting accuracy in regression | Wrong metric class | Use MAE / RMSE / R² |
| Comparing R² across datasets | Not comparable; depends on variance of y | Compare RMSE in the same units instead |
| Reporting R² alone for small datasets | Unstable, can swing dramatically | Report cross-validated R² with std |
| `LinearRegression` with collinear features | Unstable coefficients, signs flip | Drop a feature or use Ridge |
| Using normal equation on > 10⁴ features | Crawls or runs out of memory | Use SGD / mini-batch GD |
| Treating polynomial features as independent | Wrong reasoning about coefficients | Polynomials introduce by-construction collinearity |
| Forgetting `include_bias=False` with `PolynomialFeatures` + `LinearRegression` | Two intercepts, the model fits but coefficients double-count | `PolynomialFeatures(include_bias=False)` |
| Comparing models with different `n` features by R² | Larger model wins by construction | Use adjusted R² or cross-validated metric |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Default regression baseline | `LinearRegression` | Closed form, deterministic |
| Predict continuous, target outliers exist | MAE as evaluation metric | Robust to outliers |
| Predict continuous, want training to focus on big errors | RMSE / MSE as training objective | Quadratic penalty |
| Compare models with different feature counts | Adjusted R² or cross-validated RMSE | Penalises complexity |
| Non-linear relationship, low-dimensional input | Polynomial features + linear regression | Linear in parameters, simple |
| Many features, expect noise | Ridge / Lasso / Elastic Net | See `03_bias_variance_and_regularization` |
| Highly correlated features | Ridge or feature drop | Stabilises coefficients |
| Very large dataset (rows >> 10⁵, features >> 10⁴) | SGD / mini-batch | Closed form is too slow |
| Small dataset, want statistical inference | OLS with assumptions checked | Confidence intervals, p-values |
| Time-series target | Specialised models (ARIMA, state-space) | Independence assumption breaks |

---

## See also

- [01_data_and_preprocessing.md](01_data_and_preprocessing.md) — scaling, leakage, pipelines
- [03_bias_variance_and_regularization.md](03_bias_variance_and_regularization.md) — Ridge, Lasso, Elastic Net, cross-validation
- [04_classification.md](04_classification.md) — logistic regression (regression's sibling for discrete targets)
- [09_model_selection.md](09_model_selection.md) — choosing between regression models
