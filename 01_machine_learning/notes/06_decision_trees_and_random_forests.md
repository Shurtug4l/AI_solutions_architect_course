# Decision Trees and Random Forests

## Decision Trees

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

---

### Splitting Criteria

At each node, the algorithm selects the feature and threshold that maximally reduces impurity.

#### Gini Impurity (for classification)

$$G = \sum_{k=1}^{K} p_k (1 - p_k) = 1 - \sum_{k=1}^{K} p_k^2$$

$G = 0$ when the node is pure (all samples of one class). $G = 0.5$ is maximum impurity for binary classification.

#### Entropy / Information Gain (for classification)

$$H = -\sum_{k=1}^{K} p_k \log_2 p_k$$

**Information Gain** = entropy before split − weighted entropy after split.

Entropy and Gini produce similar results in practice. Gini is cheaper to compute (no log).

#### MSE / MAE (for regression)

The split that minimizes the weighted MSE of the two child nodes:

$$\text{Impurity reduction} = \text{MSE}_{\text{parent}} - \frac{n_{\text{left}}}{n} \text{MSE}_{\text{left}} - \frac{n_{\text{right}}}{n} \text{MSE}_{\text{right}}$$

---

### Prediction

- **Classification**: majority class at leaf
- **Regression**: mean (or median) of training targets at leaf

```python
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

dt = DecisionTreeClassifier(
    criterion='gini',         # 'entropy', 'log_loss'
    max_depth=None,           # None = grow until pure leaves
    min_samples_split=2,      # minimum samples to attempt a split
    min_samples_leaf=1,       # minimum samples at a leaf
    max_features=None         # features considered per split
)
```

---

### Overfitting and Pruning

Unrestricted decision trees grow until leaves are pure — they memorize training data (zero training error, poor generalization).

**Pre-pruning** (controlling growth during training):

| Parameter | Effect |
|-----------|--------|
| `max_depth` | Limits tree depth |
| `min_samples_split` | Node must have at least N samples to be split |
| `min_samples_leaf` | Leaves must have at least N samples |
| `max_leaf_nodes` | Total number of leaves |
| `min_impurity_decrease` | Split only if impurity drops by at least this value |

**Post-pruning** (cost-complexity pruning): grow a full tree, then remove subtrees that don't improve validation performance. sklearn implements this via `ccp_alpha`.

Select pruning hyperparameters via cross-validation.

---

### Feature Importance

Trees assign importance to each feature based on total impurity reduction across all splits where that feature is used, weighted by the number of samples:

$$\text{importance}(j) = \sum_{\text{nodes using } j} \frac{n_{\text{node}}}{n} \cdot \Delta \text{impurity}$$

```python
import pandas as pd
importances = pd.Series(dt.feature_importances_, index=feature_names).sort_values(ascending=False)
```

Note: this measure can be biased toward **high-cardinality** features. Use permutation importance as a more reliable alternative.

---

### Strengths and Weaknesses of Trees

| Strengths | Weaknesses |
|-----------|-----------|
| Interpretable (can be visualized) | High variance (unstable) |
| Handles mixed feature types | Axis-aligned splits miss diagonal boundaries |
| No scaling needed | Tends to overfit without pruning |
| Fast inference | Not competitive individually vs ensembles |
| Implicit feature selection | |

---

## Ensemble Methods: Motivation

A single tree has high variance. **Ensemble methods** reduce variance (or bias) by combining multiple models.

Key insight: averaging independent noisy estimators reduces variance. If each model has variance $\sigma^2$ and they are uncorrelated, the average has variance $\sigma^2 / n$.

---

## Bagging (Bootstrap Aggregating)

**Bagging** trains $B$ independent base learners on different **bootstrap samples** (random samples with replacement, same size as training set) and aggregates their predictions.

- **Classification**: majority vote
- **Regression**: mean of predictions

Each bootstrap sample uses ~63.2% of original samples; ~36.8% are out-of-bag (OOB) and can be used as a free validation set.

### Why variance is reduced

Each tree sees a different training set (due to sampling with replacement). Their errors are partially decorrelated, so the ensemble variance shrinks toward zero as $B$ grows — but bias is unchanged.

---

## Random Forests

Random forests extend bagging with **feature randomness** at each split.

At each node, only a random subset of $m_{\text{features}}$ features is considered for splitting (instead of all $n$ features).

This additional randomization further decorrelates the trees, reducing ensemble variance more than pure bagging.

**Default values** (sklearn):
- Classification: `max_features='sqrt'` → $\sqrt{n}$ features per split
- Regression: `max_features=1.0` → all features (old default was `'sqrt'`)

```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=100,          # number of trees
    max_features='sqrt',       # features per split
    max_depth=None,            # individual trees can be deep (variance averaged out)
    min_samples_leaf=1,
    bootstrap=True,
    oob_score=True,            # free OOB estimate of generalization error
    n_jobs=-1,                 # parallelize across all CPUs
    random_state=42
)
rf.fit(X_train, y_train)
print(rf.oob_score_)          # OOB accuracy
```

---

### Out-of-Bag Error

Each tree is trained on ~63% of data; the remaining ~37% (OOB samples) are used to estimate generalization. OOB error is a reliable substitute for cross-validation — no separate validation set needed.

---

### Feature Importance in Random Forests

Averaged across all trees. More stable than single-tree importance. Same high-cardinality bias applies; permutation importance is safer for interpretation.

```python
from sklearn.inspection import permutation_importance

result = permutation_importance(rf, X_test, y_test, n_repeats=10, random_state=42)
```

---

## Gradient Boosting (Brief Overview)

Unlike bagging, **boosting** trains trees sequentially: each tree corrects the residual errors of the previous ensemble. This reduces **bias** rather than variance.

- Higher accuracy than random forests on many benchmarks
- Slower to train, more hyperparameters, more prone to overfitting on noisy data
- Implementations: `sklearn.GradientBoostingClassifier`, XGBoost, LightGBM, CatBoost

**Key distinction**:
- Bagging/Random Forests: parallel, reduces variance, robust to overfitting
- Boosting: sequential, reduces bias+variance, requires careful tuning

---

## Comparison Summary

| | Single Tree | Random Forest | Gradient Boosting |
|---|---|---|---|
| Training | Fast | Moderate (parallel) | Slow (sequential) |
| Variance | High | Low | Low |
| Bias | Low (deep tree) | Low | Very Low |
| Overfitting risk | High | Low | Moderate–High |
| Interpretability | High | Low | Low |
| Best use | Baseline / demo | General purpose | Competitive accuracy |
