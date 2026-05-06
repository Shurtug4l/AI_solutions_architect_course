# Clustering

## Unsupervised Learning

Clustering is an **unsupervised** task: there are no labels. The goal is to discover inherent group structure in data based on feature similarity.

Use cases: customer segmentation, anomaly detection, document grouping, gene expression analysis, data compression (vector quantization).

---

## K-Means

### Algorithm (Lloyd's Algorithm)

1. Initialize $k$ centroids (randomly or with K-Means++)
2. **Assign** each sample to its nearest centroid
3. **Update** each centroid to the mean of its assigned samples
4. Repeat steps 2–3 until centroids stop moving (convergence)

Objective: minimize within-cluster sum of squared distances (**inertia**):

$$J = \sum_{i=1}^{k} \sum_{\mathbf{x} \in C_i} \| \mathbf{x} - \boldsymbol{\mu}_i \|^2$$

### Convergence and Local Minima

K-Means always converges but may converge to a local minimum (depends on initialization). Run multiple times with different initializations (`n_init` in sklearn) and keep the result with lowest inertia.

### K-Means++ Initialization

Instead of random initialization, K-Means++ places centroids probabilistically: each new centroid is chosen with probability proportional to its squared distance from the nearest existing centroid. This reduces the chance of poor initialization.

Default in sklearn (`init='k-means++'`).

### Choosing k: The Elbow Method

Plot inertia vs $k$. The "elbow" — where inertia stops decreasing sharply — suggests a good $k$. In practice, this inflection point is often ambiguous; combine with silhouette analysis.

```python
inertias = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    km.fit(X)
    inertias.append(km.inertia_)
```

### Limitations of K-Means

| Limitation | Why |
|-----------|-----|
| Assumes spherical clusters | Uses Euclidean distance to centroid |
| Assumes similar cluster sizes | Large clusters dominate inertia |
| Sensitive to scale | Features with large ranges dominate; always scale first |
| Requires $k$ in advance | Not always known |
| Sensitive to outliers | Centroid is the mean — pulled by extreme values |
| Cannot find non-convex shapes | E.g., concentric rings or crescent shapes |

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

km = KMeans(n_clusters=3, n_init=10, random_state=42)
labels = km.fit_predict(X_scaled)
centers = km.cluster_centers_
```

---

## Hierarchical Clustering

Builds a nested hierarchy of clusters without requiring $k$ upfront.

### Agglomerative (Bottom-Up)

1. Start: each sample is its own cluster
2. Merge the two closest clusters
3. Repeat until one cluster remains

The result is represented as a **dendrogram** — a tree diagram showing which clusters merged at what distance. Cut the dendrogram at a chosen height to get $k$ clusters.

### Linkage Methods

Define "distance between clusters" (not individual points):

| Linkage | Distance between clusters A and B |
|---------|-----------------------------------|
| **Single** | Minimum pairwise distance (nearest points) |
| **Complete** | Maximum pairwise distance (farthest points) |
| **Average** | Mean of all pairwise distances |
| **Ward** | Minimizes increase in total within-cluster variance after merge |

**Ward linkage** is the most commonly used; it tends to produce compact, equally-sized clusters (similar objective to K-Means but hierarchical).

Single linkage suffers from **chaining** (elongated clusters); complete linkage tends to break large clusters.

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

# Dendrogram
Z = linkage(X_scaled, method='ward')
dendrogram(Z)
plt.show()

# Fit for specific k
hc = AgglomerativeClustering(n_clusters=3, linkage='ward')
labels = hc.fit_predict(X_scaled)
```

### Divisive Clustering (Top-Down)

Start with all samples in one cluster and recursively split. Less common due to computational cost.

---

## DBSCAN

**Density-Based Spatial Clustering of Applications with Noise.** Groups samples that are densely packed, labels sparse regions as noise.

### Parameters

- **eps (ε)**: the maximum radius of a neighborhood
- **min_samples**: minimum number of points within ε to form a dense region

### Point Types

| Type | Definition |
|------|-----------|
| **Core point** | Has at least `min_samples` points within ε |
| **Border point** | Within ε of a core point, but not a core point itself |
| **Noise (outlier)** | Not within ε of any core point |

### Algorithm

1. For each unvisited point, retrieve its ε-neighborhood
2. If it's a core point, start a new cluster and expand it recursively (density-reachability)
3. If not a core point, mark as border (if reachable from another core) or noise

### Strengths

- Discovers clusters of arbitrary shape (not just spherical)
- Automatically identifies outliers (labeled as −1)
- Does not require $k$ in advance

### Weaknesses

- Sensitive to ε and `min_samples` — hard to set for varying-density clusters
- Struggles in high dimensions (curse of dimensionality affects neighborhood density)
- Not well-suited to clusters of very different densities

```python
from sklearn.cluster import DBSCAN

db = DBSCAN(eps=0.5, min_samples=5)
labels = db.fit_predict(X_scaled)

n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise    = list(labels).count(-1)
```

---

## Cluster Evaluation (No Ground Truth)

When true labels are unavailable, use internal metrics:

### Silhouette Score

For each sample $i$:

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

- $a(i)$: mean distance to other samples in the **same cluster** (cohesion)
- $b(i)$: mean distance to samples in the **nearest other cluster** (separation)
- Range: [−1, 1]. Higher = better. 0 means on cluster boundary. Negative means probably mis-assigned.

```python
from sklearn.metrics import silhouette_score
score = silhouette_score(X_scaled, labels)
```

### Davies-Bouldin Index

Ratio of within-cluster scatter to between-cluster separation, averaged across clusters. Lower is better. 0 = perfect.

### Calinski-Harabasz Index (Variance Ratio Criterion)

Ratio of between-cluster to within-cluster dispersion. Higher is better.

### When ground truth is available (for benchmarking)

- **Adjusted Rand Index (ARI)**: measures agreement between predicted and true labels, adjusted for chance. Range [−1, 1]; 1 = perfect.
- **Normalized Mutual Information (NMI)**: information-theoretic agreement. Range [0, 1].

```python
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
ari = adjusted_rand_score(y_true, labels)
nmi = normalized_mutual_info_score(y_true, labels)
```

---

## Algorithm Comparison

| | K-Means | Hierarchical | DBSCAN |
|---|---|---|---|
| Requires $k$ | Yes | No (choose cut height) | No |
| Cluster shape | Spherical | Flexible (depends on linkage) | Arbitrary |
| Outlier handling | None | None | Explicit (noise label) |
| Scalability | Good ($O(m \cdot k \cdot i)$) | Poor ($O(m^2)$ or $O(m^2 \log m)$) | Moderate ($O(m \log m)$ with index) |
| Deterministic | No (random init) | Yes | Yes |
| Best for | Large data, known $k$ | Hierarchy exploration, dendrograms | Spatial data, outlier detection |
