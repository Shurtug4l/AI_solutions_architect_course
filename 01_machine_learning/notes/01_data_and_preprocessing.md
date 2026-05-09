# Data and Preprocessing

## TL;DR

Every supervised ML pipeline starts with the same discipline: split data into **train / validation / test** before doing anything else, and never let the test set inform any decision until the final evaluation. **Data leakage** — fitting a scaler or imputer on the full dataset before splitting, using a feature that is a proxy for the label, shuffling time-ordered data — is the single most common cause of inflated metrics that don't survive deployment. Numerical features need **scaling** for distance- and gradient-based models (KNN, SVM, linear regression with regularisation, neural networks); tree-based models (random forests, gradient boosting) are scale-invariant. Categorical features need **encoding**: one-hot for nominal, ordinal-integer only when a meaningful order exists. Imbalanced classes ruin accuracy as a metric — switch to precision / recall / F1 / ROC-AUC and consider class weights or SMOTE. The operational rule that prevents most leakage bugs: **wrap every preprocessing step plus the model in a sklearn `Pipeline`**, so each transformer is refit only on the training portion of every CV fold.

## Cheatsheet

| Concept | sklearn / numpy | Note |
|---|---|---|
| Train/test split | `train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)` | Stratify for classification |
| Time series split | `TimeSeriesSplit` | Never shuffle time-ordered data |
| Z-score scale | `StandardScaler()` | mean 0, std 1; default for most models |
| Min-max scale | `MinMaxScaler()` | Bounded [0, 1]; sensitive to outliers |
| Robust scale | `RobustScaler()` | Median + IQR; outlier-resistant |
| One-hot | `OneHotEncoder(drop='first')` | Drop one to avoid the dummy trap in linear models |
| Ordinal | `OrdinalEncoder(categories=[...])` | Only for ordered categories |
| Mean imputation | `SimpleImputer(strategy='mean')` | Numerical, no skew |
| Mode imputation | `SimpleImputer(strategy='most_frequent')` | Categorical |
| KNN imputation | `KNNImputer(n_neighbors=5)` | Pattern-based, slower |
| Class weights | `class_weight='balanced'` | Imbalance, no resampling needed |
| Pipeline | `Pipeline([('scale', ...), ('clf', ...)])` | Prevents leakage during CV |
| Per-column transforms | `ColumnTransformer([(...), (...)])` | Different ops on numerical vs categorical |
| Log transform | `np.log1p(x)` | `log(1+x)`, safe at zero |

---

## Dataset fundamentals

A **dataset** is a collection of **samples** (rows), each described by **features** (columns) and, in supervised settings, a **label** (target).

| Term | Synonyms | Description |
|---|---|---|
| Sample | Instance, observation, example | One row |
| Feature | Attribute, variable, predictor, input | One column used for prediction |
| Label | Target, output, response | What we want to predict |

### Feature types

| Type | Subtypes | Examples | Encoding |
|---|---|---|---|
| **Numerical, continuous** | Ratio, interval | Height, temperature, price | Use directly or scale |
| **Numerical, discrete** | Count | Number of rooms, age in years | Often treat as continuous |
| **Categorical, nominal** | No order | Country, colour, job title | One-hot encoding |
| **Categorical, ordinal** | Ordered | Education level, size (S / M / L) | Ordinal encoding |
| **Binary** | — | Yes / No, True / False | 0 / 1 |

The encoding choice depends on whether the feature has a meaningful order. Treating a nominal feature as ordinal — assigning integers 0, 1, 2 to "red", "blue", "green" — implies a distance relationship that doesn't exist and confuses linear models.

---

## Train / validation / test split

The fundamental discipline of supervised ML: **never evaluate a model on data used to train it**. The standard split:

```
Full dataset
├── Training set     (60 - 80%)  → model learns from this
├── Validation set   (10 - 20%)  → hyperparameter tuning, model selection
└── Test set         (10 - 20%)  → final, one-time evaluation
```

The **test set is touched exactly once**, at the end. Using it to iterate (looking at test scores while still tuning) is data leakage by another name; you end up overfitting to the test set instead of the training set, and your reported metrics no longer predict deployed performance. With cross-validation a separate validation set is often unnecessary, but the test set still must stay held out.

For **time-series data** the splits must be **chronological** — no shuffling — or you leak future information into training. Use `TimeSeriesSplit`.

**Stratified split** preserves the class distribution in each split. Always stratify in classification, especially with imbalanced classes.

### Data leakage

Leakage is the single most common cause of inflated metrics. It happens whenever information from outside the training context contaminates the model.

Common sources:

- Scaling, imputation, or feature selection fitted on the full dataset before splitting.
- Features that are direct or indirect proxies for the label (e.g., "discharge date" when predicting hospital discharge, "credit score at decision time" when predicting loan default).
- Future data in time-series training.
- Duplicate rows split across train and test.
- Group leakage: multiple rows from the same user / patient / device split across train and test (use `GroupKFold`).

**Operational rule**: fit all transformers on training data only; then apply (transform) to validation and test. The cleanest way to enforce this is to wrap everything in a `Pipeline` and let sklearn handle the fit/transform discipline per fold during cross-validation.

---

## Missing values

### Strategies

| Strategy | When appropriate |
|---|---|
| **Drop rows** | Few missing samples, data is abundant |
| **Drop column** | Feature missing in more than ~40-50% of samples |
| **Mean / median imputation** | Numerical, missing-at-random, no strong skew (use median if skewed) |
| **Mode imputation** | Categorical features |
| **Constant imputation** | When "missing" is itself informative — fill with 0, "Unknown", etc., and consider an indicator column |
| **Model-based imputation** | KNN imputer, iterative imputer; complex but better when patterns exist |

### MCAR / MAR / MNAR

The missingness mechanism affects which strategies are safe:

- **MCAR** (Missing Completely At Random) — missingness is independent of all variables. Simple imputation is safe.
- **MAR** (Missing At Random) — missingness depends on observed variables. Conditional imputation (or model-based) is safer.
- **MNAR** (Missing Not At Random) — missingness depends on the unobserved value itself. Imputation is biased; consider an explicit indicator column to capture the signal.

When in doubt, add a binary indicator column for "was this value missing?" alongside the imputed value. The model can then learn whether missingness itself is predictive.

---

## Feature scaling

Many algorithms are sensitive to feature scale: **gradient-based** (linear / logistic regression with regularisation, neural networks), **distance-based** (KNN, SVM with RBF kernel), and **dimensionality reduction** that depends on covariance (PCA). Tree-based models (decision trees, random forests, gradient boosting) are **scale-invariant** and don't need scaling.

### StandardScaler (z-score normalisation)

$$z = \frac{x - \mu}{\sigma}$$

- Output: mean 0, standard deviation 1.
- Assumes (roughly) Gaussian distribution.
- Not bounded; sensitive to outliers because they pull $\mu$ and $\sigma$.

The default for most model classes.

### MinMaxScaler

$$x' = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$

- Output: [0, 1] (or a custom range).
- Sensitive to outliers (one extreme value compresses the rest of the range).
- Useful when bounded inputs matter (e.g., neural network inputs constrained to [0, 1] for activation functions).

### RobustScaler

$$x' = \frac{x - \text{median}}{IQR}$$

- Uses median and interquartile range.
- Resistant to outliers.
- Right choice when outliers exist and you want to keep them in the data.

### Operational pattern

Always fit scalers on training data only:

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)      # fit + transform
X_test_scaled  = scaler.transform(X_test)            # transform only
```

Inside cross-validation, this fit-on-train-only discipline is fragile to enforce by hand. Use `Pipeline` and let sklearn refit the scaler per fold automatically.

---

## Categorical encoding

### One-hot encoding (OHE)

Creates one binary column per category. Use for **nominal** features.

```
Color: [red, blue, green]   →   [is_red, is_blue, is_green]
```

- **Dummy trap**: drop one column (`drop='first'`) when feeding into linear models to avoid perfect multicollinearity (the columns sum to 1, making the design matrix rank-deficient).
- Produces sparse, high-dimensional data when cardinality is high. For high-cardinality features (city names, product IDs), consider **target encoding** (mean of the target per category, computed on training data only) or **embedding** (learned dense vectors, used in deep learning).

### Ordinal encoding

Maps categories to integers preserving order:

```
Size: [S, M, L, XL]   →   [0, 1, 2, 3]
```

Only valid when a meaningful order exists. Applying ordinal encoding to nominal features (countries, job titles) implies a numerical distance that doesn't exist and confuses linear models.

### Label encoding

Converts target labels to integers. Use **only for the target variable** in classification, never for input features (same problem as ordinal on nominal data).

---

## Class imbalance

When one class heavily outnumbers others, a model can achieve high accuracy by predicting the majority class always. A 99% accurate model on a 1%-positive dataset is exactly the trivial "predict negative" baseline.

### Detection

```python
import pandas as pd
pd.Series(y).value_counts(normalize=True)
```

If the rarest class is below ~10%, treat it as imbalanced.

### Strategies

| Strategy | Mechanism | Pros / cons |
|---|---|---|
| **Class weights** | `class_weight='balanced'` in sklearn — penalises minority misclassification more | Simple, no resampling, reproducible |
| **SMOTE** (oversampling) | Synthesise new minority samples by interpolating between near neighbours | Restores balance; can introduce noise if minority is itself heterogeneous |
| **Undersampling** | Remove majority samples | Loses information; use only when majority is huge |
| **Threshold tuning** | Adjust the decision threshold post-training | Doesn't change training, free metric trade-off |

**Metric choice matters**. Accuracy is misleading on imbalanced data. Switch to precision, recall, F1, ROC-AUC, or PR-AUC depending on which kind of error is more costly.

---

## Feature engineering

Creating new features from existing ones to expose patterns the model can't extract on its own. The line between "preprocessing" and "feature engineering" is fuzzy — both transform the input space.

Common transformations:

- **Log transform** (`np.log1p(x)`) — compresses right-skewed distributions; common for prices, counts, durations.
- **Polynomial features** (`x²`, `x₁ * x₂`) — captures non-linearity for linear models.
- **Binning** — discretise continuous values into buckets when the relationship is non-monotonic (e.g., risk by age band).
- **Date decomposition** — extract year, month, day-of-week, hour, season from timestamps.
- **Interaction terms** — product of two features when the combination is meaningful (e.g., `price * frequency`).
- **Domain ratios** — derived features like BMI = weight / height² that encode known physics or domain knowledge.

Feature engineering is domain-driven. No transformation is universally good; each must be justified by the data distribution and the model's assumptions. Tree-based models extract interactions automatically and need less engineering; linear models benefit most.

---

## Pipelines

A sklearn `Pipeline` chains preprocessing steps and the estimator. Beyond saving keystrokes, it enforces the fit-on-train-only discipline automatically — every transformer is refit on each training fold during cross-validation, and never sees validation data.

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression()),
])

pipe.fit(X_train, y_train)
pipe.score(X_test, y_test)
```

`ColumnTransformer` applies different transformations to different feature subsets — typically scaling for numerical features and one-hot for categorical:

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numerical_cols),
    ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_cols),
])

pipe = Pipeline([
    ('prep', preprocessor),
    ('clf', LogisticRegression()),
])
```

`handle_unknown='ignore'` is important for one-hot encoding in production: if a previously-unseen category appears at inference time, the encoder produces all zeros for that column instead of raising.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Scaling on the full dataset before splitting | Test scores too optimistic, fail in production | Fit scaler inside a `Pipeline`, refit per fold |
| Plain shuffle on time-series | Future leaks into past | `TimeSeriesSplit`, never shuffle |
| Same user / group in train and test | Leakage by group | `GroupKFold` |
| Imputing with mean from full dataset | Subtle leakage of test distribution | `SimpleImputer` inside a `Pipeline` |
| OHE without `handle_unknown='ignore'` | Inference fails on a new category | Set the flag |
| Dummy trap with linear models | Rank-deficient design matrix, unstable coefficients | `drop='first'` |
| Ordinal-encoding a nominal feature | Implies a false distance | Use one-hot |
| `class_weight='balanced'` plus SMOTE | Double-correction, drifts in the other direction | Pick one |
| Reporting accuracy on imbalanced data | 99% but useless | Use precision / recall / F1 / ROC-AUC |
| Tree-based model with one-hot on high-cardinality | Many tiny splits, slow training | Use `OrdinalEncoder` or category embeddings; trees handle ordinal fine |
| Dropping rows with missing values silently | Distribution shifts | Always log how many rows were dropped |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Fair generalisation estimate | Train / val / test split | Test set untouched until the end |
| Imbalanced classification split | `train_test_split(..., stratify=y)` | Preserves class proportions |
| Time-ordered data | `TimeSeriesSplit` | Forward chaining; no future-to-past leak |
| Group structure (users, patients) | `GroupKFold` | Same group never split across folds |
| Default scaling | `StandardScaler` | Works with most models, mean-centred |
| Bounded inputs (NN, image-like) | `MinMaxScaler` | Maps to [0, 1] |
| Outliers present, want to keep | `RobustScaler` | Median / IQR |
| Numerical missing, no skew | `SimpleImputer(strategy='mean')` | Fast, simple |
| Numerical missing, skewed | `SimpleImputer(strategy='median')` | Robust |
| Categorical missing | `SimpleImputer(strategy='most_frequent')` | Mode |
| Pattern-based imputation | `KNNImputer` | Better when relationships are strong |
| Nominal feature, low cardinality | `OneHotEncoder(drop='first')` | Standard |
| Nominal feature, high cardinality | Target encoding or embedding | Avoid hundreds of dummy columns |
| Ordered categories | `OrdinalEncoder` | Preserves order |
| Class imbalance, simple fix | `class_weight='balanced'` | No resampling, reproducible |
| Class imbalance, structured | SMOTE + class weights = 1 | Synthesise minority samples |
| Heterogeneous columns | `ColumnTransformer` | Per-column ops |
| Anything that goes into CV | Wrap in `Pipeline` | Prevents leakage automatically |

---

## See also

- [02_regression.md](02_regression.md) — assumptions, multicollinearity, why scaling matters for regularised regression
- [03_bias_variance_and_regularization.md](03_bias_variance_and_regularization.md) — cross-validation, leakage during regularisation
- [04_classification.md](04_classification.md) — class imbalance metrics, classification pipelines
- [05_knn.md](05_knn.md) — distance-based methods that mandate scaling
- [09_model_selection.md](09_model_selection.md) — full pipelines, nested CV
