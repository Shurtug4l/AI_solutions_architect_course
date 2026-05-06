# Classification

## Problem Formulation

Classification maps input $\mathbf{x}$ to a discrete class label $y \in \{c_1, c_2, \ldots, c_k\}$.

- **Binary**: two classes (positive / negative)
- **Multiclass**: more than two mutually exclusive classes
- **Multilabel**: each sample can belong to multiple classes simultaneously

---

## Logistic Regression

Despite the name, logistic regression is a **classification** algorithm. It models the probability of the positive class using the **sigmoid function**:

$$P(y=1 \mid \mathbf{x}) = \sigma(\mathbf{w}^T \mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w}^T \mathbf{x} + b)}}$$

The sigmoid maps any real number to $(0, 1)$, making it interpretable as a probability.

**Decision boundary**: the hyperplane where $P(y=1) = 0.5$, which corresponds to $\mathbf{w}^T \mathbf{x} + b = 0$. The boundary is linear in the feature space.

### Loss: Binary Cross-Entropy (Log Loss)

$$\mathcal{L} = -\frac{1}{m} \sum_{i=1}^{m} \left[ y_i \log(\hat{p}_i) + (1 - y_i) \log(1 - \hat{p}_i) \right]$$

- Convex → no local minima (when no regularization)
- Penalizes confident wrong predictions very heavily
- MSE is not used for classification because it creates non-convex loss landscapes with sigmoid outputs

### L1/L2 Regularization in Logistic Regression

Same formulation as in regression. `sklearn`'s `LogisticRegression` uses parameter `C = 1/λ` (higher C = less regularization).

### Multiclass with Softmax

Softmax generalizes the sigmoid to $k$ classes:

$$P(y = c_j \mid \mathbf{x}) = \frac{e^{z_j}}{\sum_{k} e^{z_k}}$$

Outputs sum to 1 across classes. Loss becomes **categorical cross-entropy**.

---

## Multiclass Strategies

When the base classifier is binary (logistic regression, SVM):

| Strategy | Approach | Models trained | Prediction |
|----------|----------|---------------|------------|
| **One-vs-Rest (OvR)** | Train one binary classifier per class | $k$ | Highest probability class |
| **One-vs-One (OvO)** | Train one classifier per pair of classes | $\binom{k}{2}$ | Majority vote across pairs |

OvR is faster; OvO can be more accurate when individual classifiers suffer from class imbalance.

---

## Confusion Matrix

For binary classification with threshold 0.5:

|  | Predicted Positive | Predicted Negative |
|--|---|---|
| **Actual Positive** | TP (True Positive) | FN (False Negative) |
| **Actual Negative** | FP (False Positive) | TN (True Negative) |

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(cm).plot()
```

---

## Classification Metrics

### Accuracy

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

Misleading on imbalanced datasets (a model predicting all-negative achieves 99% accuracy if only 1% are positive).

### Precision

$$\text{Precision} = \frac{TP}{TP + FP}$$

"Of all predicted positives, how many are actually positive?" Minimize FP when false alarms are costly (e.g., spam detection, fraud flagging in low-tolerance systems).

### Recall (Sensitivity, True Positive Rate)

$$\text{Recall} = \frac{TP}{TP + FN}$$

"Of all actual positives, how many did we catch?" Minimize FN when missing a positive is dangerous (e.g., cancer screening, fraud detection).

### F1-Score

$$F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

Harmonic mean of precision and recall. Use when both matter and classes are imbalanced. The harmonic mean punishes large gaps between precision and recall more than the arithmetic mean would.

### F_β Score

$$F_\beta = (1 + \beta^2) \cdot \frac{\text{Precision} \cdot \text{Recall}}{\beta^2 \cdot \text{Precision} + \text{Recall}}$$

- $\beta > 1$: weights recall more (e.g., medical screening, $\beta = 2$)
- $\beta < 1$: weights precision more

### Specificity (True Negative Rate)

$$\text{Specificity} = \frac{TN}{TN + FP}$$

"Of all actual negatives, how many did we correctly reject?" Used alongside sensitivity in medical diagnostics.

---

## ROC Curve and AUC

The **ROC curve** plots **True Positive Rate (Recall)** vs **False Positive Rate** as the decision threshold varies from 1 to 0.

$$\text{FPR} = \frac{FP}{FP + TN} = 1 - \text{Specificity}$$

- Top-left corner = perfect classifier
- Diagonal = random classifier
- **AUC (Area Under the Curve)**: probability that the model ranks a random positive sample higher than a random negative sample. AUC = 0.5 is random; AUC = 1.0 is perfect.

AUC is threshold-independent, making it useful for comparing models. It does not depend on class imbalance directly, but can be misleading at extreme imbalance — use the **Precision-Recall curve** in those cases.

```python
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt

fpr, tpr, thresholds = roc_curve(y_test, y_proba[:, 1])
auc = roc_auc_score(y_test, y_proba[:, 1])

plt.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel('FPR'); plt.ylabel('TPR')
```

### Precision-Recall Curve

Plots Precision vs Recall at varying thresholds. More informative than ROC when positive class is rare. High precision and high recall simultaneously is hard to achieve — the curve reveals the tradeoff.

---

## Threshold Selection

Default threshold of 0.5 is arbitrary. Adjust based on the cost of FP vs FN:

- Lower threshold → higher recall, lower precision (catch more positives, more false alarms)
- Higher threshold → higher precision, lower recall (fewer false alarms, miss more positives)

Use the PR curve or cost-sensitive analysis to select the optimal threshold for your use case.

---

## Multiclass Metrics Aggregation

With more than two classes, sklearn computes per-class metrics and aggregates:

| Average | Description | Use when |
|---------|-------------|----------|
| `macro` | Unweighted mean across classes | Classes are equally important |
| `weighted` | Mean weighted by class support | Classes have different frequencies |
| `micro` | Aggregate all TP/FP/FN, then compute | Equivalent to accuracy if all classes considered |

```python
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred, target_names=class_names))
```

---

## Logistic Regression in sklearn

```python
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(
    C=1.0,             # inverse regularization strength (higher = less regularization)
    penalty='l2',      # 'l1', 'l2', 'elasticnet', None
    solver='lbfgs',    # 'lbfgs' for multiclass; 'saga' for l1/elasticnet
    max_iter=1000,
    class_weight='balanced'   # handles imbalance
)
clf.fit(X_train, y_train)
y_pred  = clf.predict(X_test)           # class labels
y_proba = clf.predict_proba(X_test)     # probability per class
```
