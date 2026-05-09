# Decision Trees and Random Forests

## TL;DR

A **decision tree** recursively partitions the feature space with axis-aligned splits, putting a prediction at each leaf — majority class for classification, mean target for regression. The split criterion is **Gini impurity** or **entropy** for classification, **MSE** for regression; in practice Gini and entropy give similar results and Gini is cheaper. Trees are scale-invariant and handle mixed feature types natively, but a single unrestricted tree has very high variance — it grows until leaves are pure and memorises noise. **Pruning** controls this: pre-pruning via `max_depth`, `min_samples_leaf`, `min_samples_split`; post-pruning via cost-complexity (`ccp_alpha` in sklearn). **Ensembles** are the right way to use trees in production. **Bagging** trains independent trees on bootstrap samples and averages — variance drops, bias unchanged. **Random forests** add feature randomness at each split (`max_features='sqrt'` by default) to further decorrelate trees, plus a free out-of-bag (OOB) generalisation estimate. **Gradient boosting** trains trees sequentially, each correcting the previous ensemble's residuals — reduces bias too, usually wins on tabular data, but takes more tuning. The default for tabular ML in 2024 is one of XGBoost / LightGBM / CatBoost; random forest is the strong, low-tuning baseline.

## Cheatsheet

| Concept | sklearn | Note |
|---|---|---|
| Single tree (cls) | `DecisionTreeClassifier(max_depth=N)` | Always set `max_depth` or other constraint |
| Single tree (reg) | `DecisionTreeRegressor(max_depth=N)` | Same constraints apply |
| Splitting (cls) | `criterion='gini'` (default) or `'entropy'` | Similar in practice, Gini cheaper |
| Splitting (reg) | `criterion='squared_error'` | MSE-based |
| Pre-pruning | `max_depth`, `min_samples_split`, `min_samples_leaf`, `min_impurity_decrease` | Constrain growth |
| Post-pruning | `ccp_alpha` | Cost-complexity, tune via CV |
| Random forest (cls) | `RandomForestClassifier(n_estimators=100, max_features='sqrt')` | Default ensemble |
| OOB score | `oob_score=True` on RF | Free generalisation estimate |
| Feature importance | `model.feature_importances_` | Biased toward high-cardinality |
| Permutation importance | `permutation_importance(model, X, y)` | More reliable interpretation |
| Gradient boosting | XGBoost, LightGBM, CatBoost, sklearn `GradientBoostingClassifier` | Sequential, reduces bias |
| Bagging | `BaggingClassifier(base, n_estimators=...)` | Generic bagging wrapper |

---

## Decision trees

### Structure

A decision tree recursively partitions the feature space using axis-aligned splits.

```
Root node
├── Internal node (test on feature j: x_j < threshold)
│   ├── Leaf → prediction
│   └── Internal node → further splits
└── Leaf → prediction
```

Each **internal node** applies a binary test on one feature. Each **leaf node** holds a prediction: majority class (classification) or mean of target values (regression).

### Splitting criteria

At each node, the algorithm picks the feature and threshold that maximally reduces impurity (or maximises information gain).

#### Gini impurity (for classification)

$$G = \sum_{k=1}^{K} p_k (1 - p_k) = 1 - \sum_{k=1}^{K} p_k^2$$

$G = 0$ when the node is pure (all samples of one class). $G = 0.5$ is maximum impurity for binary classification.

#### Entropy / information gain (for classification)

$$H = -\sum_{k=1}^{K} p_k \log_2 p_k$$

**Information gain** = entropy before split − weighted entropy after split.

Entropy and Gini produce similar results in practice. Gini is cheaper to compute (no logarithm). Both are zero on pure nodes and maximum on uniform distributions.

#### MSE (for regression)

The split that minimises the weighted mean squared error of the two child nodes:

$$\text{Reduction} = \text{MSE}_{\text{parent}} - \frac{n_{\text{left}}}{n} \text{MSE}_{\text{left}} - \frac{n_{\text{right}}}{n} \text{MSE}_{\text{right}}$$

### Prediction

- **Classification**: majority class at the leaf.
- **Regression**: mean (or median) of training targets at the leaf.

```python
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

dt = DecisionTreeClassifier(
    criterion='gini',           # or 'entropy', 'log_loss'
    max_depth=None,             # None = grow until pure leaves (overfits)
    min_samples_split=2,        # min samples to even attempt a split
    min_samples_leaf=1,         # min samples in a leaf
    max_features=None,          # features considered per split
    random_state=42,
)
```

### Overfitting and pruning

An unrestricted decision tree grows until leaves are pure — it memorises training data, achieves zero training error, and generalises terribly. Some kind of pruning is mandatory.

**Pre-pruning** controls growth during training:

| Parameter | Effect |
|---|---|
| `max_depth` | Limits tree depth |
| `min_samples_split` | Node needs at least N samples to attempt a split |
| `min_samples_leaf` | Leaves must have at least N samples |
| `max_leaf_nodes` | Total number of leaves |
| `min_impurity_decrease` | Split only if impurity drops by at least this value |

**Post-pruning** (cost-complexity pruning, `ccp_alpha` in sklearn) grows a full tree, then collapses subtrees whose marginal contribution to validation performance falls below a complexity penalty. More principled than pre-pruning but requires a separate fitting step.

Select pruning hyperparameters via cross-validation. For random forests, individual trees can be deep because the ensemble averages out their variance.

### Feature importance

Trees assign importance to each feature based on the total impurity reduction across all splits where that feature is used, weighted by the number of samples that reach those nodes:

$$\text{importance}(j) = \sum_{\text{nodes using } j} \frac{n_{\text{node}}}{n} \cdot \Delta \text{impurity}$$

```python
import pandas as pd
importances = pd.Series(dt.feature_importances_, index=feature_names) \
    .sort_values(ascending=False)
```

This impurity-based importance can be **biased toward high-cardinality features** (continuous variables, IDs) that have more split candidates and accumulate small impurity reductions across many splits. Use **permutation importance** as a more reliable alternative — shuffle a feature's values and measure the drop in validation score; if shuffling barely affects performance, the feature isn't really being used.

### Strengths and weaknesses

| Strengths | Weaknesses |
|---|---|
| Interpretable; visualisable as a tree | High variance; small data changes flip splits |
| Handles mixed feature types out of the box | Axis-aligned splits miss diagonal boundaries |
| No scaling needed (scale-invariant) | Tends to overfit without pruning |
| Fast inference: depth-many comparisons | Not competitive individually vs ensembles |
| Implicit feature selection | Greedy: locally optimal splits, not globally optimal tree |

---

## Ensemble methods: motivation

A single tree has high variance — train it on a slightly different sample and you can get a very different model. **Ensembles** combine many models to reduce variance (or bias).

The mathematical insight: averaging $n$ uncorrelated estimators each with variance $\sigma^2$ produces an average with variance $\sigma^2 / n$. The challenge is that real ensemble members are not fully uncorrelated — bagging and random forests work by introducing controlled randomness to push correlation down.

---

## Bagging (Bootstrap Aggregating)

**Bagging** trains $B$ independent base learners on different **bootstrap samples** — random samples with replacement, same size as the original training set — and aggregates their predictions:

- **Classification**: majority vote.
- **Regression**: mean of predictions.

Each bootstrap sample uses ~63.2% of the original samples; the remaining ~36.8% are **out-of-bag (OOB)** for that tree and can serve as a free validation set.

### Why variance is reduced

Each tree sees a slightly different training set due to sampling with replacement. Their errors are partially decorrelated, so when you average them, the error variance shrinks. **Bias is unchanged** — averaging biased estimators gives a biased average. Bagging is a variance-reduction technique, not a bias-reduction technique.

---

## Random forests

Random forests extend bagging with **feature randomness at each split**: at each node, only a random subset of $m_{\text{features}}$ features (out of all $n$) is considered. This further decorrelates the trees beyond what bagging alone achieves, reducing ensemble variance more aggressively.

**Default values** (sklearn):

- Classification: `max_features='sqrt'` → $\sqrt{n}$ features per split.
- Regression: `max_features=1.0` → all features (the default has changed historically; check your version).

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=100,           # number of trees; more is better but slower
    max_features='sqrt',        # features considered per split
    max_depth=None,             # individual trees can be deep, ensemble averages variance
    min_samples_leaf=1,
    bootstrap=True,
    oob_score=True,             # free OOB estimate of generalisation error
    n_jobs=-1,                  # parallelise across all CPUs
    random_state=42,
)
rf.fit(X_train, y_train)
print(rf.oob_score_)            # OOB accuracy
```

### Out-of-bag error

Each tree was trained on ~63% of the data, so the remaining ~37% (OOB samples for that tree) form a free validation set. Aggregating OOB predictions across the forest gives a reliable estimate of generalisation error without a separate cross-validation loop.

OOB is one of random forest's quiet superpowers — for many use cases it removes the need for explicit cross-validation entirely.

### Feature importance in random forests

Averaged across all trees, more stable than single-tree importance. The same high-cardinality bias still applies; **permutation importance** is safer for interpretation:

```python
from sklearn.inspection import permutation_importance

result = permutation_importance(rf, X_test, y_test, n_repeats=10, random_state=42)
```

---

## Gradient boosting (brief overview)

Unlike bagging, **boosting** trains trees **sequentially**: each new tree corrects the residual errors of the current ensemble. The combined model becomes increasingly accurate at the cost of train-time and overfitting risk.

- Higher accuracy than random forests on most tabular benchmarks.
- Slower to train (sequential, not parallel).
- More hyperparameters (learning rate, tree count, tree depth, subsampling, regularisation).
- More prone to overfitting on noisy data — early stopping and regularisation are essential.

Implementations (in order of typical preference for tabular data):

- **XGBoost** — historically dominant, well-tuned defaults, fast.
- **LightGBM** — faster on large data via histogram-based splits and leaf-wise growth.
- **CatBoost** — best handling of categorical features out of the box.
- **sklearn `GradientBoostingClassifier`** — pure Python, slower; use `HistGradientBoostingClassifier` for the histogram-based variant.

**Key distinction** from bagging:

- Bagging / random forests: parallel, reduces **variance**, robust to overfitting.
- Boosting: sequential, reduces **bias and variance**, requires careful tuning.

---

## Comparison summary

| | Single tree | Random forest | Gradient boosting |
|---|---|---|---|
| Training | Fast | Moderate (parallel) | Slow (sequential) |
| Variance | High | Low | Low |
| Bias | Low (deep tree) | Low | Very low |
| Overfitting risk | High | Low | Moderate-High |
| Interpretability | High | Low | Low |
| Tuning effort | Low | Very low | High |
| Best use | Baseline / explanation | Strong default ensemble | Best accuracy on tabular |

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Unrestricted tree | 100% train accuracy, terrible test accuracy | Set `max_depth` or `min_samples_leaf` |
| Trees with one-hot high-cardinality features | Many tiny splits, slow training | Use `OrdinalEncoder` for trees; they handle ordinal fine |
| Reading impurity-based importance literally | High-cardinality features look artificially important | Cross-check with permutation importance |
| Random forest with too few trees | Predictions noisy | Increase `n_estimators` (100-500 is safe) |
| Random forest with `max_features=n` | Equivalent to bagging, less decorrelation | Use `'sqrt'` (cls) or 1/3 (reg) |
| Class imbalance ignored | Majority class wins | `class_weight='balanced'` or `class_weight='balanced_subsample'` |
| Boosting with high learning rate + few trees | Underfits | Lower `learning_rate`, increase `n_estimators` |
| Boosting without early stopping | Overfits silently | Hold out validation, use `early_stopping_rounds` |
| Reporting feature importance from a single random_state | Importances jitter across seeds | Average across multiple seeds, or use permutation importance |
| Comparing bagging and boosting on the same noisy data | Boosting overfits, looks worse | Tune learning rate / tree count for boosting |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Quick baseline on tabular data | Random forest | Low tuning, strong out of the box |
| Highest accuracy on tabular | XGBoost / LightGBM / CatBoost | Reduces bias too |
| Interpretability mandatory | Single decision tree | Visualisable, rule-extractable |
| Free generalisation estimate | Random forest with `oob_score=True` | No CV needed |
| Mixed numerical + categorical | Tree-based any flavour | Scale-invariant, handle types natively |
| Many noisy features | Random forest | Robust to noise |
| Small dataset, low signal | Linear model with regularisation | Trees overfit small data |
| Very large dataset, fast training | LightGBM | Histogram-based, GPU-accelerated |
| Categorical features dominant | CatBoost | Native categorical support, no manual encoding |
| Need probabilities, well-calibrated | Logistic regression or `CalibratedClassifierCV` over trees | Tree probabilities are often poorly calibrated |
| Streaming / online updates | Anything but standard trees | Trees don't update incrementally well |

---

## See also

- [01_data_and_preprocessing.md](01_data_and_preprocessing.md) — encoding strategies for categorical features
- [03_bias_variance_and_regularization.md](03_bias_variance_and_regularization.md) — variance reduction via ensembles
- [04_classification.md](04_classification.md) — alternative classifiers, evaluation metrics
- [09_model_selection.md](09_model_selection.md) — choosing between trees, forests, boosting, neural networks
