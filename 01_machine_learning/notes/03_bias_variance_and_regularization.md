# Bias, Variance, and Regularization

## The Bias-Variance Tradeoff

The expected prediction error of a model decomposes into three components:

$$\text{Error} = \text{Bias}^2 + \text{Variance} + \text{Irreducible Noise}$$

| Component | Meaning | Cause |
|-----------|---------|-------|
| **Bias** | Systematic error — model consistently misses the true relationship | Model too simple, wrong assumptions |
| **Variance** | Sensitivity to training data fluctuations | Model too complex, too few training samples |
| **Irreducible noise** | Error from measurement/labeling noise | Cannot be fixed by the model |

**Underfitting** = high bias, low variance: the model doesn't capture the signal (e.g., linear model on non-linear data).

**Overfitting** = low bias, high variance: the model memorizes training data and fails to generalize (e.g., a decision tree with no depth limit on small data).

### Diagnosing via Learning Curves

Plot train and validation error vs number of training samples:

- **Underfitting**: both train and val error are high and converge early
- **Overfitting**: train error is low, val error is much higher with a large gap
- **Good fit**: both errors are low and close together

---

## Cross-Validation

Provides a reliable estimate of generalization performance without wasting data on a fixed validation set.

### K-Fold Cross-Validation

1. Split data into $k$ equal folds
2. Train on $k-1$ folds, validate on the remaining fold
3. Repeat $k$ times (each fold serves as val once)
4. Average the validation scores

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
```

- Typical $k$: 5 or 10
- Uses all data for both training and evaluation
- More expensive: requires $k$ model fits

### Stratified K-Fold

Preserves class proportions in each fold. Essential for classification with imbalanced classes.

### Leave-One-Out (LOOCV)

$k = m$ (number of samples): each sample is a fold. Nearly unbiased but high variance and computationally expensive. Rarely used except on very small datasets.

---

## Regularization

Regularization adds a penalty term to the loss function that discourages large coefficients, controlling model complexity and reducing variance.

### Ridge Regression (L2)

$$\mathcal{L}_{\text{Ridge}} = \text{MSE} + \lambda \sum_{j=1}^{n} w_j^2$$

- Shrinks all coefficients toward zero but never exactly to zero
- Handles multicollinearity well: correlated features share the coefficient mass
- Always has a closed-form solution
- $\lambda = 0$: no regularization (plain OLS); $\lambda \to \infty$: all coefficients → 0

### Lasso Regression (L1)

$$\mathcal{L}_{\text{Lasso}} = \text{MSE} + \lambda \sum_{j=1}^{n} |w_j|$$

- Can drive coefficients exactly to zero → performs **automatic feature selection**
- Preferred when you expect only a few features to be relevant (sparse solution)
- No closed form; requires coordinate descent or subgradient methods
- Unstable when features are highly correlated (arbitrarily picks one)

### Elastic Net

$$\mathcal{L}_{\text{EN}} = \text{MSE} + \lambda_1 \sum |w_j| + \lambda_2 \sum w_j^2$$

- Combines L1 and L2 penalties
- Gets sparsity from L1 and stability with correlated features from L2
- Two hyperparameters: `alpha` (overall strength) and `l1_ratio` in sklearn

### Summary

| | L2 (Ridge) | L1 (Lasso) | Elastic Net |
|---|---|---|---|
| Feature selection | No | Yes | Partial |
| Correlated features | Shares weights | Picks one arbitrarily | Handles better |
| Solution uniqueness | Always unique | Not always unique | Unique |
| Closed form | Yes | No | No |

### Effect on coefficients

As $\lambda$ increases: coefficients shrink. Lasso creates a sparse vector; Ridge compresses all toward zero proportionally. You can visualize this with a **regularization path** (coefficient vs. log $\lambda$).

```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet

ridge = Ridge(alpha=1.0)      # alpha = lambda
lasso = Lasso(alpha=0.1)
en    = ElasticNet(alpha=0.1, l1_ratio=0.5)
```

---

## Hyperparameter Tuning

Regularization strength ($\lambda$, `alpha`) is a **hyperparameter** — not learned from data, selected via validation.

### Grid Search

Exhaustive search over a specified parameter grid:

```python
from sklearn.model_selection import GridSearchCV

param_grid = {'alpha': [0.001, 0.01, 0.1, 1, 10, 100]}
gs = GridSearchCV(Ridge(), param_grid, cv=5, scoring='neg_mean_squared_error')
gs.fit(X_train, y_train)
print(gs.best_params_)
```

Complexity: $O(|\text{grid}| \times k)$ model fits. Exponential in the number of hyperparameters.

### Randomized Search

Samples $n$ random combinations from parameter distributions. More efficient than grid search when the number of hyperparameters is large.

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import loguniform

param_dist = {'alpha': loguniform(1e-4, 1e2)}
rs = RandomizedSearchCV(Ridge(), param_dist, n_iter=50, cv=5)
rs.fit(X_train, y_train)
```

---

## Early Stopping

Applicable to iteratively trained models (gradient descent, neural networks). Stop training when the validation loss stops improving.

- Monitors val loss at each epoch; saves best checkpoint
- Equivalent to a form of L2 regularization for gradient-based models
- Avoids overfitting without modifying the loss function

```python
# Keras / TensorFlow
from tensorflow.keras.callbacks import EarlyStopping
callback = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
model.fit(X_train, y_train, validation_split=0.2, callbacks=[callback], epochs=1000)
```
