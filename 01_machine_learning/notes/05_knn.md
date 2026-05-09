# K-Nearest Neighbors (KNN)

## TL;DR

KNN is a **lazy, non-parametric, instance-based** algorithm: it doesn't really train, it just stores the training set. At inference time, it computes the distance from the query point to every training point, picks the $k$ nearest, and predicts by **majority vote** (classification) or **mean** (regression). Two operational rules: **always scale features** before KNN — the algorithm is entirely distance-based, so a feature with range [0, 10000] would dominate one with range [0, 1] — and **choose $k$ via cross-validation**, with odd values for binary classification to avoid ties. Small $k$ (1, 3) gives high-variance, locally-noisy predictions; large $k$ smooths the boundary toward high bias. The standard distance is **Euclidean (L2)**; **Manhattan (L1)** is more robust in high dimensions; **cosine** is preferred for text and direction-sensitive data. KNN suffers severely from the **curse of dimensionality** — beyond ~20-30 features, all points become approximately equidistant and the algorithm degrades. Inference cost is $O(m \cdot n)$ per query; for large training sets, KD-trees (low dimensions), Ball trees (higher), or approximate nearest-neighbour libraries (FAISS, Annoy) are necessary to keep query latency bounded.

## Cheatsheet

| Concept | sklearn / formula | Note |
|---|---|---|
| Classifier | `KNeighborsClassifier(n_neighbors=5)` | Majority vote |
| Regressor | `KNeighborsRegressor(n_neighbors=5)` | Mean of neighbours |
| Euclidean (L2) | `metric='euclidean'` (default) | `√Σ(xⱼ − x'ⱼ)²` |
| Manhattan (L1) | `metric='manhattan'` | `Σ|xⱼ − x'ⱼ|` |
| Minkowski | `metric='minkowski', p=2` | Generalises L1, L2 |
| Cosine | `metric='cosine'` | Angle, not magnitude |
| Distance-weighted | `weights='distance'` | Closer neighbours count more |
| Algorithm | `algorithm='auto'/'ball_tree'/'kd_tree'/'brute'` | sklearn picks; manual override available |
| Starting `k` | `≈ √m` | Refine via CV |
| Scaling | mandatory | Use `StandardScaler` in a `Pipeline` |
| Curse threshold | `n > ~20-30` | Degrades rapidly above |
| Inference cost | `O(m · n)` brute force | KD-tree gives `O(log m)` for low dim |

---

## Core idea

KNN is a **lazy, non-parametric** algorithm. It stores the entire training set verbatim and makes predictions at inference time by looking at the $k$ most similar training samples. There is no explicit training phase — the model **is** the training data.

This makes KNN simple to understand and impossible to "train slow", but expensive to predict (every query touches every training sample) and fragile in high dimensions.

---

## Algorithm

### Classification

1. Given a new sample $\mathbf{x}$, compute its distance to every training point.
2. Select the $k$ nearest neighbours.
3. Predict the **majority class** among those $k$ labels.

### Regression

1-2 same as above. Predict the **mean** (or weighted mean) of the $k$ neighbours' target values.

---

## Distance metrics

The choice of distance metric defines what "nearest" means; it can change the algorithm's behaviour completely. Pick the metric that matches the geometry of your data.

### Euclidean (L2)

$$d(\mathbf{x}, \mathbf{x'}) = \sqrt{\sum_{j=1}^{n} (x_j - x'_j)^2}$$

The default. Right choice for continuous numerical features that have been scaled to comparable ranges.

### Manhattan (L1)

$$d(\mathbf{x}, \mathbf{x'}) = \sum_{j=1}^{n} |x_j - x'_j|$$

More robust to outliers than Euclidean (linear penalty per dimension instead of quadratic). Often preferred in high-dimensional spaces, where Euclidean distances tend to concentrate.

### Minkowski (generalisation)

$$d(\mathbf{x}, \mathbf{x'}) = \left( \sum_{j=1}^{n} |x_j - x'_j|^p \right)^{1/p}$$

- $p = 1$: Manhattan.
- $p = 2$: Euclidean.
- $p \to \infty$: Chebyshev (max coordinate-wise difference).

In sklearn: `metric='minkowski', p=2`.

### Cosine similarity

$$\cos(\mathbf{x}, \mathbf{x'}) = \frac{\mathbf{x} \cdot \mathbf{x'}}{\|\mathbf{x}\| \cdot \|\mathbf{x'}\|}$$

Measures the angle between vectors, ignoring their magnitudes. Right choice for text data (TF-IDF, embeddings) where direction encodes meaning and absolute magnitudes are noisy. Cosine **distance** is `1 − cosine similarity`.

---

## Choosing k

$k$ is the primary hyperparameter of KNN.

- **Small $k$** (e.g., $k = 1$): very local decisions, high variance, fits noise. The decision boundary is jagged.
- **Large $k$**: smoother decision boundary, high bias. At $k = m$ (training-set size), the model always predicts the global majority class or the global mean — completely under-fit.

Select $k$ via cross-validation. In practice, **odd $k$** (5, 7, 11) avoids ties in binary classification.

**Rule of thumb to start**: $k \approx \sqrt{m}$ where $m$ is the number of training samples. CV refines from there.

---

## Feature scaling is mandatory

KNN is **entirely distance-based**. If one feature has a range of [0, 10000] and another [0, 1], the first dominates the distance computation completely and the second is effectively ignored — no matter how informative it would have been on its own scale.

**Always apply `StandardScaler` (or `MinMaxScaler` if a bounded range is preferable) before KNN.** This is non-negotiable; KNN without scaling is unreliable. The cleanest enforcement is to wrap scaler + KNN in a `Pipeline` so the scaler is refit per fold during cross-validation.

---

## Weighted KNN

Distance-weighted KNN gives closer neighbours more influence:

$$\hat{y} = \frac{\sum_{i \in N_k} w_i \cdot y_i}{\sum_{i \in N_k} w_i}, \qquad w_i = \frac{1}{d(\mathbf{x}, \mathbf{x}_i)}$$

In sklearn: `weights='distance'` (default is `'uniform'`). Distance weighting often improves accuracy at little cost; the main caveat is that it makes the algorithm more sensitive to nearby outliers.

---

## Computational complexity

| Phase | Naive KNN |
|---|---|
| Training | $O(1)$ — just store the data |
| Prediction | $O(m \cdot n)$ per query — distance to all $m$ training points in $n$ dimensions |

For large datasets, exact KNN becomes prohibitively slow. Three classes of fixes:

- **KD-trees** — efficient for low-dimensional data ($n < 20$); average $O(\log m)$ per query.
- **Ball trees** — better for higher dimensions or non-Euclidean metrics; worse-case $O(\log m)$.
- **Approximate nearest neighbours (ANN)** — FAISS, Annoy, HNSW. Trade exact correctness for orders-of-magnitude speedup at very large scale (millions to billions of points). The right choice for production-scale KNN.

sklearn picks an algorithm automatically (`algorithm='auto'`). For exact control, set `algorithm='kd_tree'`, `'ball_tree'`, or `'brute'` manually.

---

## Curse of dimensionality

As the number of features $n$ grows, all points become approximately equidistant from each other — the notion of "nearest neighbour" loses meaning. This happens because:

- The volume of a high-dimensional space grows exponentially with $n$.
- Holding a fixed fraction of the training data "nearby" requires exponentially more samples as $n$ grows.
- Distance distributions collapse: the ratio $d_{\max} / d_{\min} \to 1$ as $n \to \infty$, so the difference between the closest and farthest training point becomes meaningless.

KNN degrades rapidly beyond roughly **20-30 features** unless dimensionality reduction (PCA, t-SNE for visualisation, UMAP for embeddings) is applied first. In high-dimensional regimes, prefer methods that pick a low-dimensional informative subspace (linear models with regularisation) or that don't rely on distance at all (tree-based ensembles).

---

## sklearn reference

```python
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('knn', KNeighborsClassifier(
        n_neighbors=5,
        weights='uniform',          # or 'distance'
        metric='euclidean',         # 'manhattan', 'minkowski', 'cosine'
        algorithm='auto',           # 'ball_tree', 'kd_tree', 'brute'
    )),
])

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
```

---

## Parametric vs non-parametric (in context of KNN)

**Parametric models** (linear / logistic regression, neural networks with fixed architecture) have a fixed number of parameters regardless of training set size. The training data is discarded after learning; only the parameters are kept. Inference is fast and the model is compact.

**Non-parametric models** (KNN, kernel density estimation, decision trees without depth limits) have complexity that grows with the training data. They make fewer assumptions about the data-generating process but require the data at inference time (lazy methods) or grow in size with $m$.

KNN is the canonical example of a **lazy, non-parametric, instance-based** learner. It trades training cost (effectively zero) for inference cost (high), which is the opposite trade-off from most other ML algorithms.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Forgetting to scale features | Large-range features dominate, small-range features ignored | Always wrap in a `Pipeline` with `StandardScaler` |
| Even $k$ in binary classification | Frequent ties broken arbitrarily | Use odd $k$ (5, 7, 11) |
| $k = 1$ in production | Extremely high variance, noisy predictions | Cross-validate $k$, expect 5-30 typically |
| KNN on > 30 features without dim reduction | Predictions degrade silently | Apply PCA / feature selection first |
| KNN on millions of rows with brute force | Inference is unusably slow | KD-tree / Ball tree, or ANN library |
| Cosine distance on raw counts | Magnitude actually matters here | Use Euclidean or normalise first |
| Class imbalance | Majority class wins by default | Use `weights='distance'` or class-balanced sampling |
| Categorical features encoded as integers | Implies a false ordering | Use one-hot or define a custom distance |
| Comparing models without scaling KNN | KNN looks artificially bad | Always include the `Pipeline` |
| Setting $k$ to a constant across datasets | Optimal $k$ varies with $m$ and noise | Always cross-validate |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Small to medium dataset, complex non-linear boundary | KNN | Captures arbitrary shapes |
| Numerical features only, comparable scales | KNN with Euclidean | Default |
| High-dimensional, sparse (text) | KNN with cosine | Direction matters more than magnitude |
| Robust to outliers | KNN with Manhattan or `weights='distance'` | L1 / influence weighting |
| Large dataset, fast inference required | Anything but KNN | KNN inference is $O(m)$ per query |
| Very large dataset (millions+) where KNN is required | KNN with ANN library (FAISS, Annoy, HNSW) | Approximate, sub-linear queries |
| Feature count > 30 | Reduce dimensions first (PCA) or pick another model | Curse of dimensionality |
| Interpretability | Anything but KNN | KNN has no learned coefficients |
| Streaming / online learning | Anything but KNN | KNN can't summarise old data |
| Explainable predictions per sample | KNN with neighbour inspection | "These 5 nearest cases led to this prediction" |

---

## See also

- [01_data_and_preprocessing.md](01_data_and_preprocessing.md) — feature scaling, why distance-based methods need it
- [03_bias_variance_and_regularization.md](03_bias_variance_and_regularization.md) — choosing $k$ via CV, bias-variance tradeoff
- [04_classification.md](04_classification.md) — alternative classifiers when KNN doesn't fit
- [06_decision_trees_and_random_forests.md](06_decision_trees_and_random_forests.md) — non-parametric, scale-invariant alternative
- [09_model_selection.md](09_model_selection.md) — pipelines, hyperparameter tuning
