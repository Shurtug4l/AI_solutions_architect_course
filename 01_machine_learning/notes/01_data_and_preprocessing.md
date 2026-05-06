# Data and Preprocessing

## Dataset Fundamentals

A **dataset** is a collection of **samples** (rows), each described by **features** (columns, also called attributes or variables) and, in supervised settings, a **label** (target variable).

| Term | Synonyms | Description |
|------|----------|-------------|
| Sample | Instance, observation, example | One row |
| Feature | Attribute, variable, predictor, input | One column used for prediction |
| Label | Target, output, response | What we want to predict |

### Feature Types

| Type | Subtypes | Examples | Encoding |
|------|----------|----------|----------|
| **Numerical - Continuous** | Ratio, interval | Height, temperature, price | Use directly or scale |
| **Numerical - Discrete** | Count | Number of rooms, age in years | Often treat as continuous |
| **Categorical - Nominal** | No order | Country, color, job title | One-hot encoding |
| **Categorical - Ordinal** | Ordered | Education level, size (S/M/L) | Ordinal encoding |
| **Binary** | — | Yes/No, True/False | 0/1 |

---

## Train / Validation / Test Split

The fundamental discipline of ML: **never evaluate a model on data used to train it**.

```
Full dataset
├── Training set     (60–80%)  → model learns from this
├── Validation set   (10–20%)  → hyperparameter tuning, model selection
└── Test set         (10–20%)  → final, one-time evaluation
```

- **Test set** is touched exactly once, at the end. Using it to iterate is data leakage.
- If using cross-validation, a separate validation set is often not needed; the test set still must stay held out.
- For time-series data, splits must be **chronological** — no shuffling, or you leak future information into training.

**Stratified split**: preserves the class distribution in each split. Essential when classes are imbalanced.

### Data Leakage

Leakage means information from outside the training context contaminates the model, causing inflated metrics that do not generalize.

Common sources:
- Scaling/imputation fitted on the whole dataset before splitting
- Features that are proxies for the label (e.g., "discharge date" when predicting hospital discharge)
- Future data in time-series training

**Rule**: fit all transformers on training data only; apply (transform) to val/test.

---

## Missing Values

### Strategies

| Strategy | When appropriate |
|----------|-----------------|
| **Drop rows** | Few missing samples, data is abundant |
| **Drop column** | Feature missing in > 40–50% of samples |
| **Mean/median imputation** | Numerical features, MAR assumption, no strong skew |
| **Mode imputation** | Categorical features |
| **Constant imputation** | When "missing" is itself informative (fill with 0 or "Unknown") |
| **Model-based imputation** | (e.g., KNN imputer, iterative imputer) complex but better when patterns exist |

**MCAR / MAR / MNAR**: Missing completely at random (MCAR) is the only case where simple imputation is fully safe. In practice, always consider whether missingness carries signal (MNAR), in which case add a binary indicator column.

---

## Feature Scaling

Many algorithms are sensitive to feature scale: gradient-based methods, KNN, SVM, PCA. Tree-based models (decision trees, random forests, gradient boosting) are **scale-invariant**.

### StandardScaler (Z-score normalization)

$$z = \frac{x - \mu}{\sigma}$$

- Output: mean = 0, std = 1
- Assumes roughly Gaussian distribution
- Not bounded, sensitive to outliers

### MinMaxScaler

$$x' = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$

- Output: [0, 1] (or custom range)
- Sensitive to outliers (they compress the rest of the range)
- Good when bounded range matters (e.g., neural network inputs)

### RobustScaler

$$x' = \frac{x - \text{median}}{IQR}$$

- Uses median and interquartile range
- Resistant to outliers
- Good when the feature has outliers you want to keep

### When to scale

Always fit scalers on training data only:
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit + transform
X_test_scaled  = scaler.transform(X_test)         # only transform
```

---

## Categorical Encoding

### One-Hot Encoding (OHE)

Creates one binary column per category. Use for **nominal** features.

```
Color: [red, blue, green]  →  [is_red, is_blue, is_green]
```

- **Dummy trap**: drop one column (`drop='first'`) when using linear models to avoid perfect multicollinearity.
- Produces sparse, high-dimensional data when cardinality is high. Consider target encoding or embedding for high-cardinality features.

### Ordinal Encoding

Maps categories to integers preserving order:

```
Size: [S, M, L, XL]  →  [0, 1, 2, 3]
```

Only valid when a meaningful order exists. Applying ordinal encoding to nominal features implies a distance relationship that does not exist.

### Label Encoding

Converts target labels to integers. Use **only for the target variable** in classification, not for input features (same problem as ordinal encoding on nominal data).

---

## Class Imbalance

When one class heavily outnumbers others, a model can achieve high accuracy by predicting the majority class always.

### Detection

Check class distribution: `pd.Series(y).value_counts(normalize=True)`

### Strategies

| Strategy | Mechanism |
|----------|-----------|
| **Class weights** | Penalize misclassification of minority class more (e.g., `class_weight='balanced'` in sklearn) |
| **Oversampling (SMOTE)** | Synthesize new minority class samples via interpolation |
| **Undersampling** | Remove majority class samples |
| **Threshold tuning** | Adjust decision threshold post-training to favor recall or precision |

**Metric choice matters**: accuracy is misleading on imbalanced data. Prefer precision, recall, F1, or ROC-AUC.

---

## Feature Engineering

Creating new features from existing ones to expose patterns the model cannot extract itself.

Common transformations:
- Log transform: compresses right-skewed distributions (`np.log1p(x)`)
- Polynomial features: `x²`, `x₁ * x₂` — captures non-linearity for linear models
- Binning: discretize continuous values into buckets (useful when the relationship is non-monotonic)
- Date decomposition: extract year, month, day-of-week, hour from timestamps
- Interaction terms: product of two features when the combination is meaningful

Feature engineering is domain-driven. No transformation is universally good; each must be justified by the data distribution and the model's assumptions.

---

## Pipelines

Sklearn `Pipeline` chains preprocessing steps and the estimator, ensuring fit-only-on-train discipline is not accidentally broken:

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', LogisticRegression())
])

pipe.fit(X_train, y_train)
pipe.score(X_test, y_test)
```

`ColumnTransformer` applies different transformations to different feature subsets:

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numerical_cols),
    ('cat', OneHotEncoder(drop='first'), categorical_cols)
])
```
