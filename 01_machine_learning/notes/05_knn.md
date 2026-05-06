# K-Nearest Neighbors (KNN)

## Core Idea

KNN is a **lazy**, **non-parametric** algorithm. It stores the entire training set and makes predictions at inference time by looking at the $k$ most similar training samples.

No explicit training phase: the model *is* the training data.

---

## Algorithm

### Classification

1. Given a new sample $\mathbf{x}$, compute its distance to all training points.
2. Select the $k$ nearest neighbors.
3. Predict by **majority vote** among those $k$ labels.

### Regression

Same steps 1–2, then predict by **mean** (or weighted mean) of the $k$ neighbors' target values.

---

## Distance Metrics

The choice of distance metric is critical — it defines what "nearest" means.

### Euclidean Distance (L2)

$$d(\mathbf{x}, \mathbf{x'}) = \sqrt{\sum_{j=1}^{n} (x_j - x'_j)^2}$$

Standard choice for continuous numerical features with comparable scales.

### Manhattan Distance (L1)

$$d(\mathbf{x}, \mathbf{x'}) = \sum_{j=1}^{n} |x_j - x'_j|$$

More robust to outliers than Euclidean. Preferred in high-dimensional spaces.

### Minkowski Distance (generalization)

$$d(\mathbf{x}, \mathbf{x'}) = \left( \sum_{j=1}^{n} |x_j - x'_j|^p \right)^{1/p}$$

- $p = 1$: Manhattan; $p = 2$: Euclidean; $p \to \infty$: Chebyshev (max dimension difference)

### Cosine Similarity

$$\cos(\mathbf{x}, \mathbf{x'}) = \frac{\mathbf{x} \cdot \mathbf{x'}}{|\mathbf{x}||\mathbf{x'}|}$$

Measures angle, not magnitude. Appropriate for text data (TF-IDF vectors) or when direction matters more than absolute scale.

---

## Choosing k

$k$ is the primary hyperparameter of KNN.

- **Small $k$** (e.g., $k=1$): very local decisions, high variance, overfits noise
- **Large $k$**: smoother decision boundary, high bias, underfits — at $k = m$ the model always predicts the overall majority class/mean

Select $k$ via cross-validation. In practice, odd values of $k$ avoid ties in binary classification (e.g., $k = 5, 7, 11$).

**Rule of thumb to start**: $k \approx \sqrt{m}$ where $m$ is the number of training samples.

---

## Feature Scaling is Mandatory

KNN is entirely distance-based. If one feature has a range of [0, 10000] and another [0, 1], the first dominates the distance computation and the second is effectively ignored.

Always apply `StandardScaler` or `MinMaxScaler` before KNN.

---

## Weighted KNN

Assigns higher influence to closer neighbors:

$$\hat{y} = \frac{\sum_{i \in N_k} w_i \cdot y_i}{\sum_{i \in N_k} w_i}, \quad w_i = \frac{1}{d(\mathbf{x}, \mathbf{x}_i)}$$

In sklearn: `weights='distance'` (default is `'uniform'`).

---

## Computational Complexity

| Phase | Naive KNN |
|-------|-----------|
| Training | $O(1)$ — just store data |
| Prediction | $O(m \cdot n)$ per query — compute distance to all $m$ training points in $n$ dimensions |

For large datasets, exact KNN becomes prohibitively slow. Solutions:
- **KD-Trees**: efficient for low-dimensional data ($n < 20$), $O(\log m)$ average query
- **Ball Trees**: better for higher dimensions or non-Euclidean metrics
- **Approximate Nearest Neighbors (ANN)**: FAISS, Annoy — trade exact results for speed at very large scale

---

## Curse of Dimensionality

As the number of features $n$ grows, all points become approximately equidistant from each other. The notion of "nearest neighbor" loses meaning because:

- Volume of a high-dimensional space grows exponentially
- A fixed fraction of the training data requires exponentially more samples to be "nearby"
- Distance distributions collapse: the ratio $d_{\max}/d_{\min} \to 1$

KNN degrades rapidly beyond roughly 20–30 features unless dimensionality reduction (PCA, t-SNE) is applied first.

---

## When to Use KNN

KNN works well when:
- Dataset is small to medium (< 10k–100k samples)
- Underlying decision boundary is complex and non-linear
- Features are all numerical and on comparable scales
- No assumptions about the functional form of the relationship are warranted

KNN is a poor choice when:
- Data is high-dimensional
- Fast inference is required
- Interpretability is needed
- Training data is very large (storage and query cost)

---

## sklearn Reference

```python
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('knn', KNeighborsClassifier(
        n_neighbors=5,
        weights='uniform',   # or 'distance'
        metric='euclidean',  # 'manhattan', 'minkowski', etc.
        algorithm='auto'     # 'ball_tree', 'kd_tree', 'brute'
    ))
])

pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
```

---

## Parametric vs Non-Parametric (in context of KNN)

**Parametric models** (linear regression, logistic regression, neural networks with fixed architecture) have a fixed number of parameters regardless of training set size. The training data is discarded after learning; only the parameters are kept.

**Non-parametric models** (KNN, kernel density estimation, decision trees without depth limits) have complexity that can grow with training data. They make fewer assumptions about the data-generating process but require the data at inference time (lazy methods) or grow in complexity.

KNN is the canonical example of a **lazy, non-parametric, instance-based** learner.
