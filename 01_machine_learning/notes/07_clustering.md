# Clustering

## TL;DR

Clustering is **unsupervised**: there are no labels; the goal is to discover inherent group structure based on feature similarity. Three algorithms cover the bulk of practical use cases. **K-Means** partitions data into $k$ spherical clusters by minimising within-cluster distance to centroids — fast and scalable, but assumes spherical clusters of similar size, requires $k$ in advance, is sensitive to outliers and feature scale (always scale first), and can land in local minima (use `n_init` > 1, K-Means++ initialisation is the sklearn default). **Hierarchical clustering** builds a dendrogram by repeatedly merging the closest clusters; you get the full hierarchy for free and don't need to commit to $k$ up front, but the $O(m^2)$ complexity makes it impractical above tens of thousands of points. **DBSCAN** groups points by density — discovers clusters of arbitrary shape, automatically labels outliers as noise, doesn't need $k$, but is sensitive to its `eps` and `min_samples` parameters and struggles with clusters of varying density. Without ground truth, evaluate via the **silhouette score** (cohesion vs separation, range [-1, 1], higher is better) or **Davies-Bouldin** (lower is better); when ground truth exists, use **Adjusted Rand Index (ARI)** or **Normalized Mutual Information (NMI)**. The right algorithm depends on the cluster shape you expect: spherical → K-Means, hierarchical structure → agglomerative, arbitrary shape with outliers → DBSCAN.

## Cheatsheet

| Algorithm | sklearn | Pre-knowledge of k? | Cluster shape | Outliers |
|---|---|---|---|---|
| K-Means | `KMeans(n_clusters=k, n_init=10)` | Yes | Spherical | Sensitive |
| Mini-batch K-Means | `MiniBatchKMeans(...)` | Yes | Spherical | Sensitive |
| Agglomerative | `AgglomerativeClustering(n_clusters=k, linkage=...)` | No (cut dendrogram) | Linkage-dependent | Sensitive |
| DBSCAN | `DBSCAN(eps=ε, min_samples=N)` | No | Arbitrary | Explicit (label −1) |
| Gaussian mixture | `GaussianMixture(n_components=k)` | Yes | Elliptical (covariance) | Sensitive |

| Evaluation | sklearn | Direction | Ground truth needed? |
|---|---|---|---|
| Silhouette | `silhouette_score(X, labels)` | Higher = better, range [-1, 1] | No |
| Davies-Bouldin | `davies_bouldin_score(X, labels)` | Lower = better | No |
| Calinski-Harabasz | `calinski_harabasz_score(X, labels)` | Higher = better | No |
| Adjusted Rand Index (ARI) | `adjusted_rand_score(y_true, labels)` | Higher = better, range [-1, 1] | Yes |
| Normalized Mutual Info (NMI) | `normalized_mutual_info_score(y_true, labels)` | Higher = better, range [0, 1] | Yes |

---

## Unsupervised learning

Clustering is an **unsupervised** task: there are no labels. The algorithm is asked to discover group structure that exists in the feature distribution itself. Common applications:

- **Customer segmentation** — group buyers by behaviour for targeted campaigns.
- **Anomaly detection** — points far from any cluster are outliers worth investigating.
- **Document grouping** — bucket similar articles, news stories, or research papers.
- **Gene expression analysis** — find co-expressed gene groups.
- **Vector quantisation / data compression** — replace each point by its nearest centroid.

There is no universally "correct" clustering — different algorithms produce different groups, and the right choice depends on what you mean by "similar".

---

## K-Means

### Algorithm (Lloyd's algorithm)

1. Initialise $k$ centroids (randomly, or with K-Means++).
2. **Assign** each sample to its nearest centroid.
3. **Update** each centroid to the mean of its assigned samples.
4. Repeat steps 2-3 until centroids stop moving (convergence).

The objective minimised is the **within-cluster sum of squared distances** (also called inertia or distortion):

$$J = \sum_{i=1}^{k} \sum_{\mathbf{x} \in C_i} \| \mathbf{x} - \boldsymbol{\mu}_i \|^2$$

### Convergence and local minima

K-Means **always converges** but only to a local minimum, not necessarily the global one — the result depends on the initialisation. The standard mitigation is to run multiple times with different initialisations (`n_init` in sklearn) and keep the result with the lowest inertia.

### K-Means++ initialisation

Random initialisation can place all initial centroids near each other and produce poor clusters. K-Means++ chooses centroids probabilistically: each new centroid is chosen with probability proportional to its squared distance from the nearest existing centroid. This spreads the initial centroids and dramatically reduces the chance of poor convergence.

It is the default in sklearn (`init='k-means++'`).

### Choosing k: the elbow method

Plot inertia vs $k$. The "elbow" — the point where adding more clusters stops paying off — suggests a good $k$. In practice, this inflection point is often ambiguous; combine with the silhouette score for confirmation:

```python
inertias = []
silhouettes = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, km.labels_))
```

### Limitations of K-Means

| Limitation | Why |
|---|---|
| Assumes spherical clusters | Distance to centroid is the only criterion |
| Assumes similar cluster sizes | Large clusters dominate the inertia objective |
| Sensitive to feature scale | Always scale features first |
| Requires $k$ in advance | Not always known a priori |
| Sensitive to outliers | Centroid is the mean — pulled by extreme values |
| Cannot find non-convex shapes | Concentric rings, crescents, etc., are split incorrectly |

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

km = KMeans(n_clusters=3, n_init=10, random_state=42)
labels = km.fit_predict(X_scaled)
centers = km.cluster_centers_
```

For very large datasets, `MiniBatchKMeans` processes mini-batches and converges much faster at a small accuracy cost.

---

## Hierarchical clustering

Builds a nested hierarchy of clusters without requiring $k$ upfront.

### Agglomerative (bottom-up)

1. Start: each sample is its own cluster.
2. Merge the two closest clusters.
3. Repeat until one cluster remains.

The result is represented as a **dendrogram** — a tree diagram showing which clusters merged at what distance. **Cutting the dendrogram** at a chosen height gives $k$ clusters; cutting higher merges more, lower keeps more clusters separate.

### Linkage methods

The linkage defines distance between clusters (not individual points):

| Linkage | Distance between clusters A and B |
|---|---|
| **Single** | Minimum pairwise distance (closest points across clusters) |
| **Complete** | Maximum pairwise distance (farthest points) |
| **Average** | Mean of all pairwise distances |
| **Ward** | Minimises the increase in total within-cluster variance after merge |

**Ward linkage** is the most commonly used; it tends to produce compact, equally-sized clusters, with a similar objective to K-Means but without committing to a specific $k$.

Single linkage suffers from **chaining** — long, snake-like clusters where each member is close only to the next. Complete linkage produces more compact clusters but can break large groups apart.

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

# Visualise the dendrogram
Z = linkage(X_scaled, method='ward')
dendrogram(Z)
plt.show()

# Fit for a specific k
hc = AgglomerativeClustering(n_clusters=3, linkage='ward')
labels = hc.fit_predict(X_scaled)
```

### Divisive (top-down)

Start with all samples in one cluster and recursively split. Less common because of the computational cost — finding the optimal split at each step is itself expensive.

---

## DBSCAN

**Density-Based Spatial Clustering of Applications with Noise.** Groups densely-packed samples and labels sparse regions as noise. The first algorithm to try when clusters are non-spherical or when you want explicit outlier detection.

### Parameters

- **`eps` (ε)** — the maximum radius of a neighbourhood.
- **`min_samples`** — the minimum number of points within `eps` to form a dense region.

### Point types

| Type | Definition |
|---|---|
| **Core point** | Has at least `min_samples` neighbours within `eps` |
| **Border point** | Within `eps` of a core point, but not itself a core point |
| **Noise (outlier)** | Not within `eps` of any core point |

### Algorithm

1. For each unvisited point, retrieve its ε-neighbourhood.
2. If it's a core point, start a new cluster and expand it recursively (density-reachability).
3. If not a core point, mark as border (if reachable from another core) or noise.

### Strengths and weaknesses

**Strengths**:

- Discovers clusters of arbitrary shape (not just spherical).
- Automatically identifies outliers (labelled as `-1`).
- Does not require $k$ in advance.

**Weaknesses**:

- Sensitive to `eps` and `min_samples` — hard to set when clusters have varying density.
- Struggles in high dimensions (curse of dimensionality affects neighbourhood density).
- A single `eps` can't capture clusters with very different densities; consider HDBSCAN for that case.

```python
from sklearn.cluster import DBSCAN

db = DBSCAN(eps=0.5, min_samples=5)
labels = db.fit_predict(X_scaled)

n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise    = list(labels).count(-1)
```

A common heuristic for `eps`: plot the distance to the $k$-th nearest neighbour for each point sorted in ascending order; pick `eps` at the "knee" of the curve.

---

## Cluster evaluation (no ground truth)

When true labels are unavailable, use internal metrics — measures of cluster compactness and separation that don't require knowing the right answer.

### Silhouette score

For each sample $i$:

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

- $a(i)$ — mean distance to other samples in the **same cluster** (cohesion).
- $b(i)$ — mean distance to samples in the **nearest other cluster** (separation).
- Range: [-1, 1]. Higher is better. 0 means on a cluster boundary. Negative means probably mis-assigned.

The dataset-level silhouette is the mean of $s(i)$ across all samples.

```python
from sklearn.metrics import silhouette_score
score = silhouette_score(X_scaled, labels)
```

### Davies-Bouldin index

Average ratio of within-cluster scatter to between-cluster separation. Lower is better; 0 is perfect (impossible in practice).

### Calinski-Harabasz index (variance ratio criterion)

Ratio of between-cluster dispersion to within-cluster dispersion. Higher is better. Tends to favour solutions with more, denser clusters.

### When ground truth is available (benchmarking)

For supervised evaluation of clustering — for example, when comparing algorithms on a labelled dataset:

- **Adjusted Rand Index (ARI)** — agreement between predicted and true labels, adjusted for chance. Range [-1, 1]; 1 = perfect; ~0 = random.
- **Normalized Mutual Information (NMI)** — information-theoretic agreement. Range [0, 1].

```python
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
ari = adjusted_rand_score(y_true, labels)
nmi = normalized_mutual_info_score(y_true, labels)
```

These measure agreement up to label permutation — they don't penalise the algorithm for putting cluster A's samples in label 0 vs 1.

---

## Algorithm comparison

| | K-Means | Hierarchical | DBSCAN |
|---|---|---|---|
| Requires $k$ | Yes | No (choose cut height) | No |
| Cluster shape | Spherical | Flexible (linkage-dependent) | Arbitrary |
| Outlier handling | None | None | Explicit (noise label) |
| Scalability | Good ($O(m \cdot k \cdot i)$) | Poor ($O(m^2)$ to $O(m^2 \log m)$) | Moderate ($O(m \log m)$ with index) |
| Deterministic | No (random init) | Yes | Yes |
| Best for | Large data, known $k$, spherical groups | Hierarchy exploration, dendrograms | Spatial data, outlier detection |

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Forgetting to scale features | Large-range features dominate, others ignored | Always wrap in a `Pipeline` with `StandardScaler` |
| K-Means with `n_init=1` | Result depends heavily on lucky init | Set `n_init=10` (default in modern sklearn) |
| Choosing $k$ from elbow alone | Inflection often ambiguous | Confirm with silhouette score |
| K-Means on non-spherical clusters | Splits or merges them incorrectly | Use DBSCAN, GMM, or spectral clustering |
| DBSCAN with default `eps` | All points labelled as one cluster, or all as noise | Tune via the k-distance plot |
| DBSCAN on varying-density clusters | Either over-merges or fragments | Try HDBSCAN |
| Hierarchical on > 50k points | Memory blows up | Use sample + assign, or switch to K-Means |
| Reporting silhouette without checking range | Misinterpreting magnitudes | Score above ~0.5 is good, below ~0.25 is weak |
| Using ground-truth metrics without a held-out check | Reading too much into a single benchmark | Use multiple datasets + multiple seeds |
| Treating cluster IDs as meaningful | Cluster 0 vs cluster 1 is arbitrary | Use ARI/NMI which are permutation-invariant |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Spherical clusters, known $k$, large dataset | K-Means | Fast, scalable, well-understood |
| Very large dataset, K-Means is slow | MiniBatchKMeans | Batch updates, much faster |
| Don't know $k`, want hierarchy | Agglomerative + dendrogram | Visual cut at any granularity |
| Arbitrary shapes, noise/outliers present | DBSCAN | Density-based, explicit noise |
| Clusters of very different density | HDBSCAN | Hierarchical density |
| Need probabilistic cluster assignment | Gaussian Mixture Model | Soft assignments |
| Text or sparse high-dim data | K-Means with cosine, or spectral | Density methods break in high dim |
| Outlier detection only (not clustering per se) | Isolation Forest, Local Outlier Factor | Purpose-built |
| No ground truth, evaluate quality | Silhouette, Davies-Bouldin, Calinski-Harabasz | Internal metrics |
| Ground truth available | ARI, NMI | Permutation-invariant agreement |

---

## See also

- [01_data_and_preprocessing.md](01_data_and_preprocessing.md) — feature scaling (mandatory before all distance-based methods)
- [05_knn.md](05_knn.md) — distance-based prediction, curse of dimensionality
- [08_neural_networks.md](08_neural_networks.md) — autoencoders for dim reduction before clustering
- [09_model_selection.md](09_model_selection.md) — comparing models, choosing between paradigms
