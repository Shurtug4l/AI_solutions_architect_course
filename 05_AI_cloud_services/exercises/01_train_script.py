"""
SageMaker training entrypoint for the end-to-end clustering exercise.

This script is invoked inside the managed scikit-learn container that the
`SKLearn` estimator from the SageMaker SDK builds for us. The container injects
a fixed contract through environment variables:

    SM_CHANNEL_TRAIN  -> path where the training data CSV is mounted
    SM_MODEL_DIR      -> path where artifacts must be saved (will be tarred to S3)
    SM_OUTPUT_DIR     -> path for any other output we want to persist

Hyperparameters passed by the notebook through the estimator's `hyperparameters`
dict arrive as CLI flags (handled below with argparse). Anything we print goes
to CloudWatch and is searchable from the SageMaker job page, so we use prints
for the metrics we want to track.

Why KMeans for this exercise
----------------------------
The assignment fixes the number of clusters at 5 and the data is generated with
`make_blobs`, which produces isotropic Gaussian clusters. KMeans is the natural
fit: it assumes spherical clusters of comparable variance and converges fast on
this geometry. The alternatives we deliberately do not use are:

  - DBSCAN: density-based, would discover the number of clusters on its own,
    but the assignment requires exactly 5 clusters and DBSCAN does not give
    that guarantee.
  - Gaussian Mixture Models: more general (anisotropic covariances), but
    overkill on isotropic blobs and slower to converge.
  - Hierarchical clustering: O(n^2) memory on 10k samples is uncomfortable
    without subsampling.

Why we save centroids separately
--------------------------------
Inference at serving time can be done with just the centroids (nearest-centroid
assignment), without loading the full sklearn estimator. Persisting them as a
plain CSV makes the artifact reusable by lightweight downstream consumers that
do not want a scikit-learn dependency.
"""

import argparse
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def model_fn(model_dir):
    """Required hook for SageMaker inference containers.

    Loads the persisted KMeans estimator. Kept here so the same artifact can be
    deployed behind a SageMaker endpoint without further code changes, even if
    the assignment does not require it.
    """
    return joblib.load(os.path.join(model_dir, "model.joblib"))


if __name__ == "__main__":
    print("[INFO] Parsing arguments")
    parser = argparse.ArgumentParser()

    # Hyperparameters forwarded by the SKLearn estimator.
    parser.add_argument("--n-clusters", type=int, default=5)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-init", type=int, default=10)
    parser.add_argument("--max-iter", type=int, default=300)

    # Conventional SageMaker paths. Defaults read the env vars set by the
    # container at runtime; in a local dry-run the caller must pass them.
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "."))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN", "."))
    parser.add_argument("--train-file", type=str, default="train_data.csv")

    args, _ = parser.parse_known_args()

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------
    train_path = os.path.join(args.train, args.train_file)
    print(f"[INFO] Reading training data from {train_path}")
    train = pd.read_csv(train_path)

    # The notebook ships the synthetic dataset with a `cluster_truth` column
    # holding the ground-truth assignment from make_blobs. KMeans is
    # unsupervised, so we drop it before fitting. We keep it available if the
    # column happens to be present, otherwise we just take all numeric columns
    # as features.
    feature_cols = [c for c in train.columns if c != "cluster_truth"]
    X_train = train[feature_cols].to_numpy()
    print(f"[INFO] Training matrix shape: {X_train.shape}")

    # ------------------------------------------------------------------
    # Fit
    # ------------------------------------------------------------------
    # n_init > 1 is important: KMeans is sensitive to initialisation, and a
    # single random start can converge to a clearly suboptimal partition. The
    # default of 10 restarts is the standard mitigation.
    print(f"[INFO] Fitting KMeans with k={args.n_clusters}, n_init={args.n_init}")
    model = KMeans(
        n_clusters=args.n_clusters,
        random_state=args.random_state,
        n_init=args.n_init,
        max_iter=args.max_iter,
        verbose=1,
    )
    model.fit(X_train)

    # ------------------------------------------------------------------
    # Report training-time quality metrics
    # ------------------------------------------------------------------
    # Inertia is the sum of squared distances of each point to its centroid.
    # It is the objective KMeans minimises. It is useful as a sanity check but
    # cannot be compared across different K values without normalisation.
    print(f"[METRIC] inertia={model.inertia_:.4f}")

    # Silhouette is bounded in [-1, 1] and rewards tight, well-separated
    # clusters. It is independent of K, so it is the metric to report for
    # downstream comparisons. We subsample to keep the cost predictable in the
    # SageMaker job (silhouette is O(n^2) in the naive implementation).
    sample_size = min(2000, X_train.shape[0])
    rng = np.random.default_rng(args.random_state)
    idx = rng.choice(X_train.shape[0], size=sample_size, replace=False)
    sil = silhouette_score(X_train[idx], model.predict(X_train[idx]))
    print(f"[METRIC] silhouette_sample={sil:.4f} (n={sample_size})")

    # ------------------------------------------------------------------
    # Persist artifacts
    # ------------------------------------------------------------------
    model_path = os.path.join(args.model_dir, "model.joblib")
    joblib.dump(model, model_path)
    print(f"[INFO] Model persisted at {model_path}")

    # Centroids as a standalone CSV: one row per cluster, one column per
    # feature, plus a `cluster_id` column. Easy to consume from anything that
    # speaks CSV, no sklearn dependency required.
    centroids_path = os.path.join(args.model_dir, "centroids.csv")
    centroids = pd.DataFrame(model.cluster_centers_, columns=feature_cols)
    centroids.insert(0, "cluster_id", range(args.n_clusters))
    centroids.to_csv(centroids_path, index=False)
    print(f"[INFO] Centroids persisted at {centroids_path}")
