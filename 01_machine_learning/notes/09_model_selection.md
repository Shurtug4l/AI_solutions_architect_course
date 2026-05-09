# Model Selection and Complexity

## TL;DR

A model is **parametric** if its number of parameters is fixed in advance (linear / logistic regression, neural networks); **non-parametric** if the parameter count grows with the training data (KNN, decision trees, kernel SVM, Gaussian processes). Non-parametric doesn't mean "no parameters" — it means parameters aren't fixed up front. The **No Free Lunch theorem** is the antidote to model fanaticism: no single algorithm is best across all possible datasets, so always evaluate multiple model families on the actual data. The standard workflow: start with the simplest baseline (constant-prediction or linear), then evaluate stronger candidates in cross-validation, then tune hyperparameters of the top one or two, then a single test-set evaluation to report. **Tabular data** is dominated by gradient-boosted trees (XGBoost, LightGBM, CatBoost); random forest is the strong, low-tuning baseline; linear / logistic regression remain useful when interpretability matters or data is tiny. **Unstructured data** (images, text, audio) is dominated by neural networks. The trade-off space has three axes: **interpretability** (linear ≫ trees ≫ NN), **expressiveness** (NN ≈ boosting ≫ linear), and **computational cost** (training: NN > boosting > RF > linear; inference: KNN > NN > boosting ≈ RF > linear). Picking a model means picking your spot in this triangle; **Occam's razor in ML** says prefer the simpler model when performance is comparable, because simpler models generalise more reliably to distribution shifts.

## Cheatsheet

| Model | Tabular? | Unstructured? | Interpretability | Tuning effort |
|---|---|---|---|---|
| Linear / logistic regression | Yes (small/medium) | No | High | Low |
| Ridge / Lasso / Elastic Net | Yes | No | Medium-High | Low |
| KNN | Yes (small) | No | Low | Low |
| Decision tree | Yes (baseline / explanation) | No | High | Low |
| Random forest | Yes (default ensemble) | No | Low-Medium | Very low |
| Gradient boosting (XGB/LGBM/CB) | Yes (best) | No | Low | High |
| SVM (kernel) | Yes (medium) | Limited | Low | Medium |
| Naive Bayes | Yes (text) | Yes (text) | Medium | Very low |
| Neural network | Possible | Yes (best) | Very low | High |
| K-Means / DBSCAN | n/a (unsupervised) | n/a | Low | Low-Medium |

| Workflow step | Tool / metric |
|---|---|
| Establish baseline | `DummyClassifier` / `DummyRegressor` (constant or majority) |
| Cross-validation | `cross_val_score`, `StratifiedKFold`, `TimeSeriesSplit` |
| Compare candidates | Same CV split, same metric |
| Hyperparameter search (small space) | `GridSearchCV` |
| Hyperparameter search (large / continuous) | `RandomizedSearchCV` then Bayesian (`optuna`) |
| Final evaluation | Test set, used **once** |
| Error analysis | Confusion matrix, residual plots, sample-level inspection |

---

## Parametric vs non-parametric models

### Parametric models

A model is **parametric** if it has a **fixed, finite number of parameters** regardless of the size of the training dataset.

- The functional form is assumed in advance.
- Training data is "summarised" into the parameters; the data can be discarded after training.
- Examples: linear regression, logistic regression, Naive Bayes, neural networks with a fixed architecture.

The benefit is computational efficiency and compact storage: a logistic regression model is just a weight vector regardless of whether it was trained on 1,000 or 1,000,000 samples. The limitation is that a wrong functional assumption (e.g., assuming linearity when the relationship is non-linear) causes irreducible bias.

### Non-parametric models

A model is **non-parametric** if the number of parameters can **grow** with the training data.

- Fewer assumptions about the data-generating process.
- More flexible: complexity adapts to data size and structure.
- Examples: KNN, kernel SVM, decision trees (without depth constraints), Gaussian processes.

"Non-parametric" doesn't mean "no parameters" — it means parameters aren't fixed in advance. KNN has a hyperparameter ($k$) but no learned parameters at all; it stores the data. A decision tree has as many learned parameters (split rules) as it has nodes, which grows with data.

### Comparison

| | Parametric | Non-parametric |
|---|---|---|
| Assumptions | Strong (fixed form) | Weak |
| Training cost | Usually fast | Varies |
| Inference cost | Fast | Often slow (KNN especially) |
| Memory | Compact (just parameters) | Data-dependent |
| Bias | Can be high if form is wrong | Generally lower |
| Variance | Lower (constrained) | Can be higher |
| Good when | Functional form known, large data, speed needed | Unknown structure, small-medium data |

---

## No Free Lunch theorem

No single algorithm is universally best across all possible datasets. Every model embeds assumptions, and those assumptions help on some problem distributions and hurt on others.

Practical implication: **always evaluate multiple model families on your specific dataset**. Don't default to the latest model class because it won a benchmark on a different problem. Domain knowledge informs the prior — if you know the relationship is linear, don't reach for a neural network; if the data is high-dimensional and structured (images, text), don't expect linear models to compete.

---

## When to use which algorithm

| Model | Use when |
|---|---|
| **Linear / logistic regression** | Interpretability matters; relationship is approximately linear; very high-dimensional data (use L1 for feature selection); fast inference required |
| **Ridge / Lasso / Elastic Net** | Linear model with multicollinearity or many features; need to control variance |
| **KNN** | Small dataset; no assumption about functional form; fast prototyping; distances are meaningful in the feature space |
| **Decision tree** | Need an interpretable, explainable model; mixed feature types; rule extraction |
| **Random forest** | General-purpose tabular baseline; robust with low tuning; built-in feature importance and OOB score |
| **Gradient boosting (XGBoost / LightGBM / CatBoost)** | Highest accuracy on tabular data; willing to tune; data is not tiny |
| **Neural network** | Unstructured data (images, text, audio); very large datasets; manual feature engineering is expensive |
| **SVM (kernel)** | Moderate-sized datasets; high-dimensional spaces; clear margin separation |
| **K-Means / DBSCAN** | Unsupervised grouping; no labels available |
| **Naive Bayes** | Text classification; very fast; works surprisingly well with small data and many features |

In 2024, on tabular data with structured features, **gradient boosting wins** in most empirical comparisons. On unstructured data (images, language, audio), **neural networks win** by a wide margin. The choice between paradigms is rarely close — it's usually clear which family the data belongs to.

---

## Model complexity and expressiveness

**Expressiveness** = the range of functions a model can represent.

- A linear model can only represent hyperplanes → low expressiveness.
- A deep neural network or an unconstrained decision tree can approximate almost any function → high expressiveness.

More expressive models require more data to train reliably without overfitting. The key question is whether you have enough signal in enough data to justify the model's complexity.

**Occam's razor in ML**: prefer the simpler model when performance is comparable. Simpler models generalise more reliably to distribution shifts, are easier to debug, faster at inference, and don't require deep learning expertise to maintain.

---

## Interpretability vs performance

| Model | Interpretability | Typical performance |
|---|---|---|
| Linear / logistic | High (coefficient = feature contribution) | Baseline |
| Decision tree | High (visualisable rules) | Moderate |
| KNN | Low (instance-based, no summary; you can show the nearest training points) | Moderate |
| Random forest | Low-Medium (feature importance, not rules) | Good |
| Gradient boosting | Low | Very good |
| Neural network | Very low | State-of-the-art (unstructured data) |

Post-hoc interpretability tools (**SHAP** for additive explanations, **LIME** for local approximations) can add partial explainability to black-box models but do not fully substitute for inherently interpretable models. SHAP values for tree-based models are exact and fast (`TreeSHAP`), which is one reason gradient boosting plus SHAP is the dominant tabular pipeline today.

---

## Computational considerations

| | Training | Inference | Memory |
|---|---|---|---|
| Linear / logistic | $O(m \cdot n)$ | $O(n)$ | $O(n)$ |
| KNN | $O(1)$ (just store data) | $O(m \cdot n)$ per query | $O(m \cdot n)$ |
| Decision tree | $O(m \cdot n \log m)$ | $O(\log m)$ | $O(\text{nodes})$ |
| Random forest | $B \times O(m \cdot \sqrt{n} \log m)$ | $B \times O(\log m)$ | $B \times O(\text{nodes})$ |
| Neural network | $O(E \cdot m \cdot P)$ | $O(P)$ | $O(P)$ |

Symbols: $m$ = samples, $n$ = features, $B$ = trees, $E$ = epochs, $P$ = parameters.

KNN's training cost is zero, but every query touches every training point — production-scale KNN needs approximate nearest-neighbour libraries (FAISS, Annoy, HNSW). Neural network training cost is dominated by the number of epochs times the parameter count; inference cost is just $O(P)$ per sample, which is why even a billion-parameter model can serve queries quickly with the right hardware.

---

## Practical model selection workflow

```
1. Understand the problem
   ├── Supervised / unsupervised?
   ├── Classification / regression?
   ├── What metric matters? (F1? MAE? AUC? business cost?)
   └── Constraints (latency, interpretability, data size, regulatory)

2. Establish a baseline
   └── Simplest possible model: DummyClassifier (majority class),
       DummyRegressor (mean prediction), or a single linear model.
       Always know how a stupid baseline performs.

3. Evaluate candidates via cross-validation
   ├── Start with: linear / logistic, random forest, gradient boosting
   ├── Add a neural network only for unstructured data or when nothing else suffices
   └── Add complexity only if simpler models underfit

4. Tune hyperparameters of the top 1-2 candidates
   └── RandomizedSearchCV first (broad sweep), then GridSearchCV (fine)
       or jump to Optuna for continuous / mixed spaces

5. Evaluate on the held-out test set ONCE
   └── Report performance, confidence intervals if needed

6. Analyse errors
   └── Where does the model fail? Is there a pattern?
       Often the next 5% accuracy comes from feature engineering
       informed by error analysis, not from a fancier model.
```

The order matters. Tuning hyperparameters before establishing a baseline tells you nothing about whether the model class is right for the problem. Touching the test set during iteration silently overfits to it and breaks the entire experimental setup.

---

## Scikit-Learn estimator interface

All sklearn models follow the same interface, which lets you swap them inside a pipeline or grid search without changing the surrounding code:

```python
model.fit(X_train, y_train)             # learn from data
model.predict(X_test)                   # output labels / values
model.predict_proba(X_test)             # output class probabilities (classifiers)
model.score(X_test, y_test)             # default metric (accuracy / R²)
model.get_params()                      # view hyperparameters
model.set_params(**params)              # set hyperparameters
```

This uniform API is one of sklearn's biggest practical contributions — it makes "try five models" a one-line change instead of five separate adapters.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Picking a model based on a benchmark from a different domain | Wrong tool for the job | Always evaluate on your own data |
| Skipping the dummy baseline | Don't know if "good" is actually good | Always include `DummyClassifier` / `DummyRegressor` |
| Touching the test set during iteration | Inflated metrics, fail in production | Test set is touched once at the very end |
| Comparing models across different CV splits | Comparing apples and oranges | Same `cv` splitter, same `random_state` |
| Tuning on the test set | Same as above, hidden version | Tune on validation or via nested CV |
| Choosing the model with highest CV mean ignoring std | Lucky model on this seed, unstable | Compare mean ± std; prefer the one with smaller std at similar mean |
| Reaching for neural networks on tabular data | Worse than gradient boosting, more tuning | Default to GBM unless data is unstructured |
| Reaching for linear regression on highly non-linear data | High bias, mediocre fit | Move to trees / boosting / NN |
| Using accuracy on imbalanced classification | Misleading | Use F1 / AUC / per-class metrics |
| Reporting one number without confidence interval | Overstates certainty | Report mean ± std or bootstrap CI |
| Ignoring inference latency | Model wins offline, fails in production | Include latency budget in the selection criterion |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Tabular data, default | Gradient boosting (XGBoost / LightGBM / CatBoost) | Best accuracy on most tabular benchmarks |
| Tabular data, low-tuning baseline | Random forest | Strong out of the box, OOB score for free |
| Tabular data, interpretability mandatory | Linear / logistic regression with regularisation | Coefficients are explanations |
| Tabular data, very few samples | Linear model + regularisation | Trees / NN overfit small data |
| Images, audio, video | CNN, vision transformer | Learned spatial features |
| Text classification | Transformer fine-tuning, or TF-IDF + linear | Modern: transformer; baseline: linear |
| Text classification, very fast | Naive Bayes on n-grams | Surprisingly strong baseline |
| Unsupervised grouping | K-Means (spherical) / DBSCAN (arbitrary shape) | Pick on cluster geometry |
| Anomaly detection | Isolation Forest, LOF, DBSCAN | Purpose-built for outliers |
| Need probabilities, well-calibrated | Logistic regression, or `CalibratedClassifierCV` over trees | Tree probabilities often miscalibrated |
| Need to explain individual predictions | SHAP on the trained model | TreeSHAP is fast and exact for tree models |
| Hard latency budget | Linear, single tree, small NN distilled | Inference cost first, accuracy second |
| Streaming / online learning | SGDClassifier / SGDRegressor, river | Update without retraining from scratch |

---

## See also

- [01_data_and_preprocessing.md](01_data_and_preprocessing.md) — pipelines, leakage prevention
- [02_regression.md](02_regression.md) — linear / polynomial regression in depth
- [03_bias_variance_and_regularization.md](03_bias_variance_and_regularization.md) — cross-validation, hyperparameter tuning
- [04_classification.md](04_classification.md) — classification metrics, threshold tuning
- [05_knn.md](05_knn.md) — KNN as the canonical lazy non-parametric baseline
- [06_decision_trees_and_random_forests.md](06_decision_trees_and_random_forests.md) — tree ensembles in depth
- [07_clustering.md](07_clustering.md) — unsupervised model choice
- [08_neural_networks.md](08_neural_networks.md) — when neural networks are the right call
