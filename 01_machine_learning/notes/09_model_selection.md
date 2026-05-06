# Model Selection and Complexity

## Parametric vs Non-Parametric Models

### Parametric Models

A model is **parametric** if it has a **fixed, finite number of parameters** regardless of the size of the training dataset.

- The functional form is assumed in advance
- Training data is "summarized" into the parameters; the data can be discarded after training
- Examples: linear regression, logistic regression, naïve Bayes, neural networks with fixed architecture

The benefit is computational efficiency and compact storage: a logistic regression model is just a weight vector regardless of whether it was trained on 1,000 or 1,000,000 samples.

The limitation is that a wrong functional assumption (e.g., assuming linearity when the relationship is non-linear) causes irreducible bias.

### Non-Parametric Models

A model is **non-parametric** if the number of parameters can grow with training data.

- Fewer assumptions about the data-generating process
- More flexible: complexity adapts to data
- Examples: KNN, kernel SVM, decision trees (without depth constraints), Gaussian processes

Note: "non-parametric" does not mean "no parameters" — it means parameters are not fixed in advance. KNN has a hyperparameter ($k$) but no learned parameters at all (it stores data). A decision tree has as many parameters (split rules) as nodes, which grows with data.

### Comparison

| | Parametric | Non-Parametric |
|---|---|---|
| Assumptions | Strong (fixed form) | Weak |
| Training cost | Usually fast | Varies |
| Inference cost | Fast | Often slow (KNN) |
| Memory | Compact (just parameters) | Data-dependent |
| Bias | Can be high if form is wrong | Generally lower |
| Variance | Lower (constrained) | Can be higher |
| Good when | Functional form known, large data, speed needed | Unknown structure, small-medium data |

---

## No Free Lunch Theorem

No single algorithm is universally best across all possible datasets. Every model makes assumptions, and those assumptions will be beneficial in some problem distributions and harmful in others.

Practical implication: always evaluate multiple model families on your specific dataset. Domain knowledge informs the prior — if you know the relationship is linear, don't default to a neural network.

---

## When to Use Which Algorithm

| Model | Use When |
|-------|---------|
| **Linear / Logistic Regression** | Interpretability needed; relationship is approximately linear; high-dimensional data (L1 for feature selection); fast inference |
| **Ridge / Lasso** | Linear model with multicollinearity or many features; need to control variance |
| **KNN** | Small dataset; no assumption about form; fast prototyping; distances are meaningful |
| **Decision Tree** | Need an interpretable, explainable model; mixed feature types; rule extraction |
| **Random Forest** | General-purpose, tabular data; robust baseline; built-in feature importance |
| **Gradient Boosting (XGBoost, LightGBM)** | Highest accuracy on tabular data; willing to tune; data is not tiny |
| **Neural Network** | Unstructured data (images, text, audio); very large datasets; feature engineering is expensive |
| **SVM (kernel)** | Moderate-sized datasets; high-dimensional spaces; clear margin separation |
| **K-Means / DBSCAN** | Unsupervised grouping; no labels available |
| **Naïve Bayes** | Text classification; very fast; works well with small data and many features |

---

## Model Complexity and Expressiveness

**Expressiveness** = the range of functions a model can represent.

- A linear model can only represent hyperplanes → low expressiveness
- A deep neural network or an unconstrained decision tree can approximate almost any function → high expressiveness

More expressive models require more data to train reliably without overfitting. The key question is whether you have enough signal in enough data to justify the model's complexity.

**Occam's Razor in ML**: prefer the simpler model when performance is comparable. Simpler models generalize more reliably to distribution shifts.

---

## Interpretability vs Performance

| Model | Interpretability | Typical Performance |
|-------|-----------------|---------------------|
| Linear / Logistic | High (coefficient = feature contribution) | Baseline |
| Decision Tree | High (visualizable rules) | Moderate |
| KNN | Low (instance-based, no summary) | Moderate |
| Random Forest | Low–Medium (feature importance, not rules) | Good |
| Gradient Boosting | Low | Very good |
| Neural Network | Very Low | State-of-the-art (unstructured data) |

Post-hoc interpretability tools (SHAP, LIME) can add partial explainability to black-box models but do not fully substitute for inherently interpretable models.

---

## Computational Considerations

| | Training | Inference | Memory |
|---|---|---|---|
| Linear / Logistic | $O(m \cdot n)$ | $O(n)$ | $O(n)$ |
| KNN | $O(1)$ (store data) | $O(m \cdot n)$ | $O(m \cdot n)$ |
| Decision Tree | $O(m \cdot n \log m)$ | $O(\log m)$ | $O(\text{nodes})$ |
| Random Forest | $B \times O(m \cdot \sqrt{n} \log m)$ | $B \times O(\log m)$ | $B \times O(\text{nodes})$ |
| Neural Network | $O(E \cdot m \cdot P)$ | $O(P)$ | $O(P)$ |

$m$ = samples, $n$ = features, $B$ = trees, $E$ = epochs, $P$ = parameters.

---

## Practical Model Selection Workflow

```
1. Understand the problem
   ├── Supervised / unsupervised?
   ├── Classification / regression?
   ├── What metric matters (F1? MAE? AUC?)
   └── Constraints (latency, interpretability, data size)

2. Establish a baseline
   └── Simplest possible model (linear, majority class, mean prediction)

3. Evaluate candidates via cross-validation
   ├── Start with: Linear/Logistic, Random Forest, Gradient Boosting
   └── Add complexity only if simpler models underfit

4. Tune hyperparameters of top candidates
   └── RandomizedSearchCV → GridSearchCV for fine-tuning

5. Evaluate on held-out test set (once)
   └── Report performance, confidence intervals if needed

6. Analyze errors
   └── Where does the model fail? Is there a pattern?
```

---

## Scikit-Learn Estimator Interface

All sklearn models follow the same interface, enabling easy swapping:

```python
model.fit(X_train, y_train)           # learn from data
model.predict(X_test)                 # output labels / values
model.predict_proba(X_test)           # output class probabilities (classifiers)
model.score(X_test, y_test)           # default metric (accuracy / R²)
model.get_params()                    # view hyperparameters
model.set_params(**params)            # set hyperparameters
```

This uniformity means you can swap models inside a Pipeline or GridSearchCV without changing the surrounding code.
