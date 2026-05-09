# Bias, Variance, and Regularization

## TL;DR

The expected error of a model decomposes into three pieces: **bias** (systematic mistakes from a model that's too simple), **variance** (sensitivity to the specific training set), and **irreducible noise** (uncertainty inherent to the data). Underfitting is the high-bias regime; overfitting is the high-variance regime. **Regularization** adds a penalty on the size of the weights to the loss function, trading a bit of bias for a large reduction in variance. **L1 (Lasso)** drives small coefficients exactly to zero, giving free feature selection. **L2 (Ridge)** shrinks coefficients smoothly toward zero without eliminating them, which is the right behavior under multicollinearity. **Elastic Net** combines the two. The penalty strength (`λ` in textbooks, `alpha` in scikit-learn) is a hyperparameter tuned via cross-validation. Two operational rules to internalize: always **scale features** before fitting a regularized model (the penalty is unit-sensitive), and always wrap the scaler and the model in a single `Pipeline` so the scaler is refit per fold and never sees validation data.

## Cheatsheet

| Concept | Formula / sklearn class | When it helps |
|---|---|---|
| Bias-variance decomposition | `Error = Bias² + Var + σ²` | Reasoning about under/overfitting |
| K-fold CV | `cross_val_score(model, X, y, cv=5)` | Stable generalization estimate without a fixed holdout |
| Stratified K-fold | `StratifiedKFold(n_splits=5)` | Classification with imbalanced classes |
| LOOCV | `LeaveOneOut()` | Very small datasets only (slow, high variance) |
| Time series CV | `TimeSeriesSplit(n_splits=5)` | Time-ordered data, prevents future leaking into past |
| Ridge (L2) | `Ridge(alpha=λ)` — `MSE + λ Σ wⱼ²` | Multicollinearity, smooth shrinkage, no feature drop |
| Lasso (L1) | `Lasso(alpha=λ)` — `MSE + λ Σ |wⱼ|` | Sparse weights, automatic feature selection |
| Elastic Net | `ElasticNet(alpha, l1_ratio)` | Sparse + stable when correlated features are present |
| Grid search | `GridSearchCV(model, param_grid, cv)` | Few discrete hyperparameters |
| Random search | `RandomizedSearchCV(model, dist, n_iter, cv)` | Many or continuous hyperparameters |
| Early stopping | `EarlyStopping(patience=10, restore_best_weights=True)` | Iteratively trained models (NN, GBM) |

---

## Bias-variance decomposition

For a model trained on a random sample, the expected prediction error at a new point splits into three terms:

$$\text{Error} = \text{Bias}^2 + \text{Variance} + \text{Irreducible Noise}$$

Intuitively, **bias** is how wrong your predictions are on average across all possible training sets — a measure of the model class's inability to capture the true relationship. **Variance** is how much your predictions wiggle as you swap in a different training sample of the same size. **Irreducible noise** is the floor set by labelling errors and unobserved variables; no model can drive the total error below it.

| Component | Meaning | Cause |
|---|---|---|
| **Bias** | Systematic error — the model class consistently misses the true relationship | Model too simple, wrong assumptions, or strong implicit constraints |
| **Variance** | Sensitivity to fluctuations in the training data | Model too flexible relative to sample size |
| **Irreducible noise** | Error from measurement or labelling noise | Inherent to the data; cannot be reduced by changing the model |

**Underfitting** = high bias, low variance — the model fails to capture the signal even on the training set (e.g., a linear model on clearly non-linear data).

**Overfitting** = low bias, high variance — the model memorises the training data, including its noise, and generalises poorly (e.g., an unconstrained decision tree on a small dataset).

### Diagnosis via learning curves

The fastest way to tell which regime you're in is to plot training error and validation error as a function of training-set size:

- **Underfitting**: both curves are high and converge early to a plateau. Adding data won't help; you need a more expressive model class or better features.
- **Overfitting**: training error is low, validation error is much higher, and the gap stays large or grows. Adding data, regularising, or simplifying the model all help.
- **Good fit**: both curves are low and close together.

---

## Cross-validation

A single train/validation split gives one number, which can be lucky or unlucky depending on which samples ended up where. **Cross-validation averages the score over multiple splits**, producing a more reliable estimate of generalisation while reusing all the data for both training and evaluation.

### K-fold

The standard recipe:

1. Split the data into $k$ equal folds.
2. For each fold, train on the remaining $k-1$ folds and evaluate on the held-out fold.
3. Average the $k$ validation scores.

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5,
                         scoring='neg_mean_squared_error')
```

Typical $k$: 5 or 10. The cost is $k$ model fits, which adds up for expensive models and large grids.

### Stratified K-fold

Plain K-fold can produce folds where one class is rare or missing, which destabilises classification metrics. **Stratified K-fold preserves class proportions in every fold** and is the default choice for any classification task, especially imbalanced ones.

```python
from sklearn.model_selection import StratifiedKFold
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
```

### LOOCV

Leave-one-out is the extreme case where $k = m$ (each sample is its own fold). It's nearly unbiased but has high variance and costs as many fits as you have samples. Reserve it for very small datasets (under ~100 samples) where every example matters.

### Time series

Time-ordered data breaks the i.i.d. assumption that K-fold relies on: shuffling allows information from the future to leak into the training set. Use a forward-chaining split that always trains on the past and validates on the future:

```python
from sklearn.model_selection import TimeSeriesSplit
cv = TimeSeriesSplit(n_splits=5)
```

---

## Regularization

Regularization adds a penalty term to the loss function that grows with the size of the weights. Minimising the penalised loss yields a model that fits the data well but keeps its weights small — a trade that increases bias slightly while reducing variance substantially. Both common penalties depend on the **absolute magnitude** of the weights, so features measured in different units (millimetres vs kilometres, or 0–1 vs 0–10⁶) produce wildly different penalty contributions. **Always standardise features (mean 0, std 1) before fitting a regularised model**, and do it inside a `Pipeline` so the scaler is refit per fold during CV.

### Ridge (L2)

$$\mathcal{L}_{\text{Ridge}} = \text{MSE} + \lambda \sum_j w_j^2$$

- Shrinks coefficients smoothly toward zero, but **never exactly to zero**.
- Handles multicollinearity well: when two features are highly correlated, the L2 penalty distributes the weight between them rather than picking one arbitrarily.
- Has a closed-form solution, so it is fast and deterministic.
- $\lambda = 0$ recovers plain ordinary least squares; as $\lambda \to \infty$ all coefficients tend to 0.

### Lasso (L1)

$$\mathcal{L}_{\text{Lasso}} = \text{MSE} + \lambda \sum_j |w_j|$$

- Drives small coefficients **exactly to zero**, performing automatic feature selection.
- Best when you expect only a few features to matter and the rest are noise (a "sparse" signal).
- No closed form; sklearn solves it with coordinate descent.
- Unstable under correlated features: if two predictors carry the same information, Lasso picks one essentially at random and discards the other, and the choice can flip between folds.

### Elastic Net

$$\mathcal{L}_{\text{EN}} = \text{MSE} + \lambda_1 \sum |w_j| + \lambda_2 \sum w_j^2$$

- Combines L1 and L2: you get sparsity from L1 and stability from L2.
- Two hyperparameters in sklearn: `alpha` (overall strength) and `l1_ratio` (the mix between L1 and L2; 0 is pure Ridge, 1 is pure Lasso).
- A reasonable default when you expect a sparse solution but worry about correlated features.

```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet

ridge = Ridge(alpha=1.0)        # alpha is the textbook λ
lasso = Lasso(alpha=0.1)
en    = ElasticNet(alpha=0.1, l1_ratio=0.5)
```

### Comparison

| | Ridge (L2) | Lasso (L1) | Elastic Net |
|---|---|---|---|
| Feature selection | No | Yes (sparse) | Partial |
| Correlated features | Distributes weight | Picks one arbitrarily | Distributes, with optional sparsity |
| Solution uniqueness | Always | Not guaranteed | Yes |
| Closed form | Yes | No | No |

As $\lambda$ increases, all coefficients shrink. Lasso produces a **sparse** weight vector (many exact zeros); Ridge compresses every coefficient toward zero proportionally. Plotting coefficient values against $\log \lambda$ gives the **regularization path** — a useful diagnostic for understanding which features survive at each penalty level.

---

## Hyperparameter tuning

The penalty strength ($\lambda$, `alpha`) is a hyperparameter — not learned from data, chosen via validation. The choice should be made on data the model has not seen, otherwise you optimise toward the validation set and inflate your estimate of how well the model will generalise.

### Grid search

Exhaustive search over a fixed grid of values:

```python
from sklearn.model_selection import GridSearchCV

param_grid = {'alpha': [0.001, 0.01, 0.1, 1, 10, 100]}
gs = GridSearchCV(Ridge(), param_grid, cv=5,
                  scoring='neg_mean_squared_error')
gs.fit(X_train, y_train)
print(gs.best_params_)
```

Cost: $|\text{grid}| \times k$ fits. The grid grows multiplicatively with the number of hyperparameters, which limits grid search to two or three dimensions in practice. Use **log-spaced** grids for penalty strengths since the interesting variation is in orders of magnitude.

### Randomized search

Samples $n$ random combinations from probability distributions over the hyperparameters. More efficient than grid search when the search space is large or continuous, because most hyperparameters have a few sensitive values surrounded by indifferent ones; sampling explores those flat regions less.

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import loguniform

param_dist = {'alpha': loguniform(1e-4, 1e2)}
rs = RandomizedSearchCV(Ridge(), param_dist, n_iter=50, cv=5)
rs.fit(X_train, y_train)
```

For mixed continuous/discrete spaces and more than four or five hyperparameters, Bayesian optimization (`optuna`, `scikit-optimize`) is dramatically more sample-efficient.

---

## Early stopping

Iteratively trained models — neural networks, gradient boosting, gradient-descent linear models — minimise training loss on every step. Without intervention, the validation loss eventually starts to climb again as the model fits noise. Early stopping monitors validation loss and halts training when it stops improving for a configurable number of consecutive evaluations (`patience`).

```python
from tensorflow.keras.callbacks import EarlyStopping

callback = EarlyStopping(monitor='val_loss',
                         patience=10,
                         restore_best_weights=True)

model.fit(X_train, y_train,
         validation_split=0.2,
         callbacks=[callback],
         epochs=1000)
```

`restore_best_weights=True` is essential: without it, training ends with the weights from the worst recent epoch, not the best one observed. Conceptually, early stopping plays the same role as L2 regularization for gradient-based models — it prevents the weights from growing unbounded, achieving a similar bias-variance trade-off without modifying the loss function.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Scaling features outside CV (fitting the scaler on the full `X`) | Validation data has leaked into training via the fitted scaler; CV scores are too optimistic | Wrap scaler and model in a `Pipeline`; sklearn refits the scaler on each training fold |
| Plain K-fold on imbalanced classification | Some folds end up missing a class entirely; metrics swing wildly | Use `StratifiedKFold` |
| K-fold on time-ordered data | Future samples leak into the training set, validation score is too optimistic | Use `TimeSeriesSplit` |
| Forgetting to scale before Ridge or Lasso | The penalty is unit-sensitive, large-scale features dominate the loss | Always scale (StandardScaler or RobustScaler) before regularisation |
| Confusing `alpha` (sklearn) with $\lambda$ (textbook) | Same quantity, different name; cross-checking notes feels inconsistent | Note the convention; in sklearn `alpha = λ` |
| Lasso on highly correlated features | Picks one feature seemingly at random, the choice flips across folds | Use Elastic Net (or remove redundant features upstream) |
| Grid search on continuous hyperparameters | Coarse, blind to local optima between grid points | Use random search or a log-spaced grid |
| Early stopping without `restore_best_weights` | The model returned is from a degraded epoch, not the best one | Always set `restore_best_weights=True` |
| LOOCV on a large dataset | Cost explodes ($m$ fits) and variance is still high | Use 5- or 10-fold instead |
| Using the same `random_state` in every component | Cross-validated scores look more stable than they are | Vary seeds across folds when checking robustness |

---

## When to use what

| Situation | Technique | Why |
|---|---|---|
| Multicollinearity (correlated features) | Ridge | Distributes weight across correlated predictors instead of picking one |
| Automatic feature selection | Lasso | Drives uninformative coefficients exactly to zero |
| Few features expected to matter, many noise features | Lasso or Elastic Net | Sparse solutions are easier to interpret and faster at inference |
| Correlated features and you want sparsity | Elastic Net | Combines L1 sparsity with L2 stability |
| Iterative model with plateauing val loss | Early stopping | No loss-function changes, free regularisation effect |
| Few discrete hyperparameters | Grid search | Exhaustive, deterministic, easy to reason about |
| Continuous hyperparameters or > 4 dimensions | Random search (then Bayesian) | Better coverage with the same compute budget |
| Tiny dataset (< 100 samples) | LOOCV | Uses every sample for evaluation; bias is minimal |
| Imbalanced classification | Stratified K-fold | Keeps class proportions stable across folds |
| Time-ordered data | `TimeSeriesSplit` | Respects chronology, prevents temporal leakage |
| Production pipeline | `Pipeline(scaler, model)` always inside CV | Scaler refit per fold, no leakage from validation data |

---

## See also

- [02_regression.md](02_regression.md) — OLS, the unregularised baseline (Ridge with $\lambda = 0$)
- [04_classification.md](04_classification.md) — equivalent regularisation in logistic regression (`C = 1/λ`)
- [08_neural_networks.md](08_neural_networks.md) — early stopping, dropout, weight decay in practice
- [09_model_selection.md](09_model_selection.md) — full pipelines, nested CV, model comparison
