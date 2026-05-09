# Classification

## TL;DR

Classification maps an input to a **discrete class label**. The classical baseline is **logistic regression** — despite the name, it's a classification algorithm: it produces a probability via the **sigmoid** (binary) or **softmax** (multiclass) function and is trained with **cross-entropy** loss. Cross-entropy is convex (no local minima for unregularised models) and penalises confidently-wrong predictions heavily, which is why MSE is not used here. Five metrics drive evaluation: **accuracy** (misleading on imbalanced data), **precision** (minimise false positives), **recall** (minimise false negatives), **F1** (harmonic mean of the two), and **ROC-AUC** (threshold-independent ranking quality). The choice between precision and recall is application-specific: minimise FP when false alarms are costly (spam filtering), minimise FN when missed positives are dangerous (cancer screening). For multiclass with a binary base classifier, **One-vs-Rest** trains $k$ classifiers and is fast; **One-vs-One** trains $\binom{k}{2}$ classifiers and can be more accurate when individual binary classifiers struggle with imbalance. The default decision threshold of 0.5 is arbitrary — tune it on the precision-recall curve to match the operational cost of FP vs FN.

## Cheatsheet

| Concept | Formula / sklearn | Note |
|---|---|---|
| Logistic regression | `LogisticRegression(C=1.0, penalty='l2')` | `C = 1/λ`, higher C = less regularisation |
| Sigmoid | `σ(z) = 1 / (1 + e⁻ᶻ)` | Maps real to (0, 1) |
| Softmax | `softmax(zⱼ) = eᶻʲ / Σ eᶻᵏ` | Multiclass probabilities, sum to 1 |
| Loss (binary) | Binary cross-entropy / log loss | Convex with sigmoid |
| Loss (multiclass) | Categorical cross-entropy | Convex with softmax |
| OvR (multiclass) | `LogisticRegression(multi_class='ovr')` | Train k binary classifiers |
| OvO (multiclass) | `OneVsOneClassifier(...)` | Train C(k, 2) classifiers |
| Confusion matrix | `confusion_matrix(y, y_pred)` | TP, FP, FN, TN |
| Accuracy | `(TP + TN) / total` | Misleading on imbalance |
| Precision | `TP / (TP + FP)` | False-alarm cost |
| Recall (sensitivity) | `TP / (TP + FN)` | Missed-positive cost |
| F1 | `2 PR / (P + R)` | Balanced precision-recall |
| F_β | `(1+β²) PR / (β²P + R)` | β > 1 weights recall, β < 1 weights precision |
| ROC-AUC | `roc_auc_score(y, y_proba)` | Threshold-independent |
| PR-AUC | `average_precision_score(y, y_proba)` | Better than ROC for rare positives |
| Class weights | `class_weight='balanced'` | Imbalance correction |

---

## Problem formulation

Classification maps an input $\mathbf{x}$ to a discrete class label $y \in \{c_1, c_2, \ldots, c_k\}$.

- **Binary** — two classes (positive / negative).
- **Multiclass** — more than two mutually exclusive classes.
- **Multilabel** — each sample can belong to multiple classes simultaneously (e.g., a news article tagged "tech", "politics", "AI").

Multiclass is the default extension of binary classification; multilabel requires different metrics and architectures (one binary classifier per label is the simplest baseline).

---

## Logistic regression

Despite the name, logistic regression is a **classification** algorithm. It models the probability of the positive class using the **sigmoid function**:

$$P(y = 1 \mid \mathbf{x}) = \sigma(\mathbf{w}^T \mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x} + b)}}$$

The sigmoid maps any real number to $(0, 1)$, making it interpretable as a probability. The **decision boundary** — the hyperplane where $P(y=1) = 0.5$, equivalently where $\mathbf{w}^T \mathbf{x} + b = 0$ — is **linear** in the feature space. Logistic regression cannot learn non-linear boundaries on its own; it needs polynomial / interaction features or a non-linear model class for that.

### Loss: binary cross-entropy (log loss)

$$\mathcal{L} = -\frac{1}{m} \sum_{i=1}^{m} \left[ y_i \log(\hat{p}_i) + (1 - y_i) \log(1 - \hat{p}_i) \right]$$

- **Convex** when there's no regularisation, so optimisation has a unique minimum.
- Penalises confidently-wrong predictions very heavily ($-\log(p)$ goes to infinity as $p \to 0$).
- MSE is **not** used for classification because composing MSE with a sigmoid produces a non-convex loss surface with bad local minima.

### L1 / L2 regularisation in logistic regression

Same formulation as in regression. Sklearn's `LogisticRegression` uses parameter `C = 1/λ` (higher C means weaker regularisation):

```python
LogisticRegression(C=0.1)       # strong regularisation
LogisticRegression(C=10)        # weak regularisation
```

### Multiclass with softmax

Softmax generalises the sigmoid to $k$ classes:

$$P(y = c_j \mid \mathbf{x}) = \frac{e^{z_j}}{\sum_{k} e^{z_k}}$$

Outputs sum to 1 across classes. The training loss becomes **categorical cross-entropy**, which is also convex with softmax outputs.

---

## Multiclass strategies

When the base classifier is binary (logistic regression, SVM with linear kernel), there are two standard strategies for handling more than two classes:

| Strategy | Approach | Models trained | Prediction |
|---|---|---|---|
| **One-vs-Rest (OvR)** | Train one binary classifier per class | $k$ | Highest probability class |
| **One-vs-One (OvO)** | Train one classifier per pair of classes | $\binom{k}{2}$ | Majority vote across pairs |

OvR is faster and uses simpler classifiers. OvO trains more models but each one only sees two classes, which can be more accurate when individual classifiers suffer from imbalance against a heterogeneous "rest". Modern logistic regression in sklearn supports native multinomial training (with softmax), which is usually preferable to wrapping a binary classifier in OvR.

---

## Confusion matrix

For binary classification with threshold 0.5:

|  | Predicted Positive | Predicted Negative |
|---|---|---|
| **Actual Positive** | TP | FN |
| **Actual Negative** | FP | TN |

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm).plot()
```

The confusion matrix is the foundation for every other classification metric — internalise the four cells and the rest follows.

---

## Classification metrics

### Accuracy

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

Misleading on imbalanced datasets: a model predicting "negative" always achieves 99% accuracy on a dataset with 1% positives, but is useless. Default to other metrics on any imbalanced problem.

### Precision

$$\text{Precision} = \frac{TP}{TP + FP}$$

"Of all predicted positives, how many are actually positive?" Maximise precision when **false alarms are costly** — spam filtering (you don't want to lose real email), fraud flagging in low-tolerance systems, recommendation surfaces where bad recs erode trust.

### Recall (sensitivity, true positive rate)

$$\text{Recall} = \frac{TP}{TP + FN}$$

"Of all actual positives, how many did we catch?" Maximise recall when **missing a positive is dangerous** — cancer screening, fraud detection, threat detection. The cost of a missed positive far exceeds the cost of a false alarm.

### F1-score

$$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

Harmonic mean of precision and recall. Use when both matter and classes are imbalanced. The harmonic mean punishes large gaps between precision and recall more than the arithmetic mean would, so an F1 of 0.8 implies both metrics are reasonably high (you can't get F1 = 0.8 with precision 0.99 and recall 0.1).

### F-β score

$$F_\beta = (1 + \beta^2) \cdot \frac{\text{Precision} \cdot \text{Recall}}{\beta^2 \cdot \text{Precision} + \text{Recall}}$$

- $\beta > 1$ weights **recall** more (e.g., medical screening, $\beta = 2$).
- $\beta < 1$ weights **precision** more.

Use F2 when missing a positive is twice as costly as a false alarm; use F0.5 when a false alarm is twice as costly. Picking $\beta$ is an explicit business decision.

### Specificity (true negative rate)

$$\text{Specificity} = \frac{TN}{TN + FP}$$

"Of all actual negatives, how many did we correctly reject?" Used alongside sensitivity in medical diagnostics and other high-stakes binary classification.

---

## ROC curve and AUC

The **ROC curve** plots **true positive rate (recall)** vs **false positive rate** as the decision threshold sweeps from 1 to 0:

$$\text{FPR} = \frac{FP}{FP + TN} = 1 - \text{Specificity}$$

- Top-left corner = perfect classifier.
- Diagonal = random classifier.
- **AUC** (Area Under the Curve) is the probability that the model ranks a random positive sample higher than a random negative sample. AUC = 0.5 is random; AUC = 1.0 is perfect.

AUC is **threshold-independent**, which makes it useful for comparing models without committing to a specific operational threshold. It does not depend on class imbalance directly, but can be **misleading at extreme imbalance** — a high AUC on a 0.1%-positive dataset can still leave you with poor precision-recall tradeoffs at any actual operating point. Use the **Precision-Recall curve** in those cases.

```python
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt

fpr, tpr, thresholds = roc_curve(y_test, y_proba[:, 1])
auc = roc_auc_score(y_test, y_proba[:, 1])

plt.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel('FPR')
plt.ylabel('TPR')
```

### Precision-recall curve

Plots Precision vs Recall at varying thresholds. **More informative than ROC when the positive class is rare** (TN dominates the FPR denominator and inflates the AUC even for poor models). High precision and high recall simultaneously is hard to achieve — the curve reveals exactly where the trade-off lies.

`average_precision_score` summarises the PR curve as a single number (PR-AUC), the right "AUC" to report on imbalanced problems.

---

## Threshold selection

The default threshold of 0.5 is **arbitrary**. Adjust based on the operational cost of FP vs FN:

- **Lower threshold** → higher recall, lower precision (catch more positives, more false alarms).
- **Higher threshold** → higher precision, lower recall (fewer false alarms, miss more positives).

Use the PR curve or a cost-sensitive analysis (cost of FP × number of FP + cost of FN × number of FN) to select the optimal threshold for your specific use case. Tuning the threshold is often the cheapest way to make a model "better" by your real metric.

---

## Multiclass metrics aggregation

With more than two classes, sklearn computes per-class metrics and aggregates them according to one of three averaging strategies:

| Average | Description | When to use |
|---|---|---|
| `macro` | Unweighted mean across classes | Treat all classes as equally important |
| `weighted` | Mean weighted by class support | Reflect actual class frequencies |
| `micro` | Aggregate all TP / FP / FN globally, then compute | Equivalent to accuracy when all classes are considered |

```python
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred, target_names=class_names))
```

The classification report shows precision, recall, F1, and support per class plus the three averages — it's the right starting point for any multiclass evaluation.

---

## Logistic regression in sklearn

```python
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(
    C=1.0,                          # inverse regularisation strength (higher = less regularisation)
    penalty='l2',                   # 'l1', 'l2', 'elasticnet', None
    solver='lbfgs',                 # 'lbfgs' for default; 'saga' for l1/elasticnet; 'liblinear' for binary l1
    max_iter=1000,
    class_weight='balanced',        # handles imbalance; sets weights inversely proportional to frequencies
)
clf.fit(X_train, y_train)
y_pred  = clf.predict(X_test)               # class labels
y_proba = clf.predict_proba(X_test)         # probability per class
```

For multinomial / softmax behaviour explicitly: `multi_class='multinomial'` (the default in modern sklearn).

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| Reporting accuracy on imbalanced data | 99% accuracy, useless model | Use precision / recall / F1 / PR-AUC |
| Forgetting to scale before regularised logistic regression | Penalty applied unevenly | Always scale (in a `Pipeline`) |
| Using ROC-AUC on extreme imbalance | High AUC, poor real-world performance | Use PR-AUC instead |
| Default threshold 0.5 in production | Wrong precision-recall trade-off | Tune threshold on validation curve |
| `class_weight='balanced'` plus SMOTE | Double correction, drift in opposite direction | Pick one |
| Calling `predict_proba` on calibrated-only when you need calibrated probs | Probabilities not well calibrated | Use `CalibratedClassifierCV` |
| Confusing `C` with `λ` | Stronger regularisation needs **smaller** C in sklearn | Remember `C = 1/λ` |
| Treating multiclass as multilabel | Probabilities don't sum to 1 properly | Use the right loss / model setup |
| Macro F1 on imbalanced classes | Rare classes count equally, low signal-to-noise | Use weighted F1 or per-class breakdown |
| `solver='liblinear'` with multiclass | Forces OvR, can be suboptimal | Use `lbfgs` or `saga` for multinomial |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Linear baseline classifier | `LogisticRegression` | Convex, fast, interpretable |
| Need probabilities, not just labels | `predict_proba` | Cost-sensitive thresholds, calibration |
| Cost of false positive >> false negative | Optimise precision; threshold up | Spam, recommendations |
| Cost of false negative >> false positive | Optimise recall; threshold down | Cancer screening, fraud |
| Both matter, balance them | F1 (or F_β with chosen β) | Single number summary |
| Compare classifiers without committing to threshold | ROC-AUC | Threshold-independent |
| Compare classifiers on rare-positive task | PR-AUC | More informative than ROC at imbalance |
| Imbalanced classes | `class_weight='balanced'` | No resampling |
| Severe imbalance | SMOTE + class weights = 1, OR threshold tuning | Synthesise minority samples |
| Multiclass with linear model | Native multinomial logistic regression | Default, optimal |
| Multiclass with binary-only base classifier | OvR (fast) or OvO (more accurate, slower) | Wrap with `OneVsRestClassifier` / `OneVsOneClassifier` |
| Per-class diagnostics | `classification_report` | Quick view of every metric and class |

---

## See also

- [01_data_and_preprocessing.md](01_data_and_preprocessing.md) — class imbalance strategies, scaling
- [02_regression.md](02_regression.md) — linear regression, MSE, contrast with classification loss
- [03_bias_variance_and_regularization.md](03_bias_variance_and_regularization.md) — `C = 1/λ`, regularisation in logistic regression
- [05_knn.md](05_knn.md) — non-linear classifier, mandates feature scaling
- [09_model_selection.md](09_model_selection.md) — cross-validation, hyperparameter tuning for classifiers
