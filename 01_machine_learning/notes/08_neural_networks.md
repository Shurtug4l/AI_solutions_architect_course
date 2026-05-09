# Neural Networks

## TL;DR

A neural network is a stack of **dense (linear) layers** separated by **non-linear activations**: without the non-linearity, any number of linear layers collapses to a single linear transformation. The **Universal Approximation Theorem** says one hidden layer with enough neurons can approximate any continuous function — but in practice depth matters, because deeper networks express some functions exponentially more efficiently than shallow ones. **ReLU** (`max(0, z)`) is the default hidden-layer activation — fast, no saturation for positives, prone to "dying" if pre-activations stay negative; switch to Leaky ReLU / ELU / GELU when that happens. Output layer: **sigmoid** for binary classification, **softmax** for multiclass, **linear** for regression. Training optimises a loss (cross-entropy for classification, MSE for regression) via **backpropagation** — the chain rule applied systematically backward through the layers — combined with **mini-batch SGD** or, more commonly today, **Adam**. Three operational levers fight overfitting: **early stopping** (most important — `restore_best_weights=True`), **dropout** (typical rate 0.2-0.5), and **batch normalisation** (stabilises training, allows higher learning rates). The vanishing-gradient problem in deep sigmoid/tanh networks is the historical reason ReLU + good initialisation (He for ReLU, Glorot for tanh) + batch norm + residual connections all became standard.

## Cheatsheet

| Concept | Formula / Keras | Note |
|---|---|---|
| Dense layer | `Dense(n, activation='relu')` | Linear + activation |
| Sigmoid | `1 / (1 + e^-z)`, range (0, 1) | Binary output |
| Tanh | range (-1, 1) | Hidden (legacy) |
| ReLU | `max(0, z)` | Default hidden activation |
| Leaky ReLU | `max(αz, z)`, α ≈ 0.01 | Fixes dying ReLU |
| Softmax | normalises to probability vector | Multiclass output |
| Linear | identity | Regression output |
| Loss (regression) | MSE | `loss='mse'` |
| Loss (binary cls) | Binary cross-entropy | `loss='binary_crossentropy'` |
| Loss (multiclass) | Categorical cross-entropy | `loss='sparse_categorical_crossentropy'` (int labels) |
| Optimiser default | Adam | `optimizer='adam'` or `Adam(learning_rate=1e-3)` |
| Backprop | chain rule, computed automatically | Frameworks handle it |
| Mini-batch | `batch_size=32-512` | 32-128 default |
| Epoch | one full pass over the training set | `epochs=N` |
| Dropout | `Dropout(p)`, p in [0.2, 0.5] | Off at inference |
| Batch norm | `BatchNormalization()` | Mean 0, std 1 per mini-batch + learned γ, β |
| Weight decay (L2) | Add to loss / use AdamW | Regularisation |
| Early stopping | `EarlyStopping(patience=N, restore_best_weights=True)` | Always set restore_best |
| He init | `kernel_initializer='he_normal'` | For ReLU |
| Glorot (Xavier) init | `kernel_initializer='glorot_uniform'` (default) | For tanh / sigmoid |

---

## Perceptron

The perceptron is the foundational unit of a neural network. It computes a weighted sum of inputs and passes it through an activation function:

$$\hat{y} = f\left(\sum_{j=1}^{n} w_j x_j + b\right) = f(\mathbf{w}^T \mathbf{x} + b)$$

The original perceptron used a **step function** (threshold activation), making it a binary linear classifier. It can only represent linearly separable functions — the famous XOR limitation that put neural network research on hold until non-linear activations and multi-layer networks were established.

---

## Multi-layer perceptron (MLP)

A **feedforward neural network** composed of:

- **Input layer** — one node per feature.
- **Hidden layers** — intermediate representations; apply a non-linear activation.
- **Output layer** — one node per output (or one node per class in multiclass).

```
Input → [Dense + Activation] → ... → [Dense + Activation] → Output
```

With at least one hidden layer and a non-linear activation, an MLP can approximate any continuous function — the **Universal Approximation Theorem**. The catch is the theorem says nothing about how wide the layer needs to be, or whether you can train the weights to find the approximation. In practice **depth matters**: deeper networks can represent some functions exponentially more efficiently than shallow ones, and modern training techniques (residual connections, normalisation, careful initialisation) are what make deep architectures trainable.

---

## Activation functions

Non-linearity is essential. Without it, any number of stacked linear layers collapses to a single linear transformation: $W_3 W_2 W_1 \mathbf{x}$ is just a different linear map.

### Sigmoid

$$\sigma(z) = \frac{1}{1 + e^{-z}} \in (0, 1)$$

- Output as probability — used in binary output layers.
- **Saturates** at 0 and 1 → **vanishing gradient** when stacked in hidden layers (the derivative is at most 0.25, multiplying many of them together produces a gradient that effectively vanishes).
- Not zero-centred — outputs always positive, which can slow optimisation.

### Tanh

$$\tanh(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}} \in (-1, 1)$$

- Zero-centred, better than sigmoid for hidden layers.
- Still saturates, still has the vanishing gradient at extremes.
- Largely superseded by ReLU in modern networks.

### ReLU (Rectified Linear Unit)

$$\text{ReLU}(z) = \max(0, z)$$

- The default for hidden layers.
- No saturation for positive values → faster convergence, gradient is exactly 1.
- Computationally cheap (no exponentials).
- **Dying ReLU**: neurons that consistently receive negative pre-activations output zero permanently and stop learning (zero gradient through the unit).

### Leaky ReLU / ELU / GELU

$$\text{Leaky ReLU}(z) = \max(\alpha z, z), \quad \alpha \approx 0.01$$

Fixes dying ReLU by allowing a small gradient for negative values. **ELU** has a smooth negative part and pushes mean activations toward zero. **GELU** (used in transformers) is smooth everywhere and empirically performs well in modern architectures.

### Softmax (output layer for multiclass)

$$\text{softmax}(z_j) = \frac{e^{z_j}}{\sum_k e^{z_k}}$$

Converts a vector of logits to a probability distribution that sums to 1. Used **exclusively in output layers**, never in hidden layers.

### Summary

| Activation | Range | Use case |
|---|---|---|
| Sigmoid | (0, 1) | Binary output |
| Tanh | (-1, 1) | Hidden layers (legacy) |
| ReLU | [0, ∞) | Hidden layers (default) |
| Leaky ReLU | (-∞, ∞) | Hidden layers (when dying ReLU is a concern) |
| ELU / GELU | (-∞, ∞) | Hidden layers (modern alternatives) |
| Softmax | (0, 1), sums to 1 | Multiclass output |
| Linear | (-∞, ∞) | Regression output |

---

## Forward pass

Computation flows left-to-right through the network. For layer $l$:

$$\mathbf{z}^{(l)} = \mathbf{W}^{(l)} \mathbf{a}^{(l-1)} + \mathbf{b}^{(l)}$$
$$\mathbf{a}^{(l)} = f\left(\mathbf{z}^{(l)}\right)$$

where $\mathbf{a}^{(0)} = \mathbf{x}$ (the input), $\mathbf{W}^{(l)}$ are the layer's weights, and $\mathbf{b}^{(l)}$ is the bias vector.

---

## Loss functions

| Task | Loss | Formula |
|---|---|---|
| Regression | MSE | $\frac{1}{m}\sum(y - \hat{y})^2$ |
| Binary classification | Binary cross-entropy | $-[y \log \hat{p} + (1-y) \log(1-\hat{p})]$ |
| Multiclass | Categorical cross-entropy | $-\sum_k y_k \log \hat{p}_k$ |

Cross-entropy paired with sigmoid / softmax outputs produces a **convex** loss landscape (for the unregularised model), which is why these pairings are the standard. MSE with sigmoid outputs is non-convex and badly conditioned — never use it for classification.

---

## Backpropagation

Backpropagation is the algorithm for computing gradients of the loss with respect to all weights efficiently, using the **chain rule**.

1. **Forward pass**: compute activations at each layer, store them.
2. **Compute the loss** at the output.
3. **Backward pass**: propagate the gradient of the loss back through each layer.

For layer $l$:

$$\frac{\partial \mathcal{L}}{\partial \mathbf{W}^{(l)}} = \frac{\partial \mathcal{L}}{\partial \mathbf{z}^{(l)}} \cdot \left(\mathbf{a}^{(l-1)}\right)^T$$

This gives the gradient needed to update each weight via gradient descent.

**Why the chain rule**: the loss depends on the network's output, which depends on the next-to-last layer's activations, which depend on its weights, and so on backward. Backprop applies the chain rule systematically from the output backward to the input. Modern frameworks (TensorFlow, PyTorch, JAX) compute backprop automatically via **automatic differentiation** — you write the forward pass, the framework derives the gradients.

---

## Optimisers

### SGD (Stochastic Gradient Descent)

$$\mathbf{w} \leftarrow \mathbf{w} - \eta \nabla_{\mathbf{w}} \mathcal{L}$$

Simple but slow convergence; requires careful learning rate tuning. Rarely used as-is for deep networks, but underlies all modern variants.

### SGD with momentum

Accumulates a velocity vector in the direction of persistent gradients:

$$\mathbf{v} \leftarrow \gamma \mathbf{v} + \eta \nabla_{\mathbf{w}} \mathcal{L}$$
$$\mathbf{w} \leftarrow \mathbf{w} - \mathbf{v}$$

Dampens oscillations, accelerates in consistent gradient directions. Typical $\gamma = 0.9$. Often the best choice for very large training runs (e.g., training LLMs from scratch).

### Adam (Adaptive Moment Estimation)

Combines momentum (first moment of gradients) with per-parameter adaptive learning rates (second moment):

$$m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t$$
$$v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2$$
$$\mathbf{w} \leftarrow \mathbf{w} - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

Default hyperparameters: $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$.

- Robust to noisy gradients, sparse features, varying gradient magnitudes.
- The **default choice** for most deep learning tasks today.
- **AdamW** is a variant that decouples weight decay from the gradient update; preferred for transformer-style models.

### RMSProp

Divides the learning rate by a running mean of recent gradient magnitudes. Predecessor to Adam (Adam's second moment is RMSProp's running mean). Still useful for recurrent networks where gradient magnitudes vary widely.

---

## Training concepts

### Epochs and batches

- **Epoch** — one full pass through the training dataset.
- **Batch size** — number of samples per gradient update.
  - Smaller batches → noisier gradient estimates (acts as regularisation), more updates per epoch, slower per epoch.
  - Larger batches → more accurate gradient, fewer updates per epoch, faster per epoch (especially on GPUs), less regularising.

Typical batch sizes: 32-128 for small/medium models, 256-2048 for large models on modern hardware. Doubling batch size while doubling learning rate is a useful first heuristic when scaling up.

### Vanishing gradient problem

In deep networks with sigmoid or tanh activations, gradients shrink exponentially through layers during backprop (because the derivative of sigmoid is at most 0.25, and you multiply many of them along the chain). Early layers receive near-zero gradients and effectively stop learning.

Fixes that became standard precisely because of this problem:

- **ReLU activations** — gradient is 1 for positive values, doesn't shrink.
- **Batch normalisation** — reduces internal covariate shift, stabilises gradients.
- **Residual connections** (skip connections in ResNets) — provide shortcuts that bypass many layers, so gradients flow back without multiplying through every weight.
- **Careful weight initialisation** — He initialisation for ReLU, Glorot (Xavier) for tanh.

---

## Regularisation in neural networks

### Dropout

During training, randomly set a fraction $p$ of neuron activations to zero at each forward pass. This prevents co-adaptation of neurons (the network can't rely on any single neuron being available) and acts as training an ensemble of many subnetworks.

- Disabled at inference time (all neurons active, activations scaled by $1-p$ to compensate).
- Typical rates: 0.2-0.5 for hidden layers; 0.1-0.2 for input layers if used at all.

### Batch normalisation

Normalises the activations of each layer across the mini-batch (zero mean, unit variance), then applies learned scale and shift parameters $\gamma, \beta$:

$$\hat{z} = \frac{z - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}} \cdot \gamma + \beta$$

Benefits: stabilises training, allows higher learning rates, reduces sensitivity to initialisation, acts as mild regularisation.

For very small batches or transformer-style architectures, **layer normalisation** (normalising across features rather than across the batch) is preferred.

### L2 regularisation (weight decay)

Add $\lambda \sum w^2$ to the loss. In SGD, this is equivalent to multiplying weights by $(1 - \lambda \eta)$ before each update. Standard regularisation when dropout is insufficient; pairs especially well with **AdamW**, which separates the decay from the gradient-based update.

### Early stopping

Stop training when validation loss stops improving for a number of consecutive epochs (`patience`). The single most important regularisation technique — it's free, doesn't change the loss, and prevents the model from training past the validation minimum:

```python
keras.callbacks.EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True,      # essential — keep the best epoch's weights
)
```

---

## Keras quick reference

```python
import tensorflow as tf
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(n_features,)),
    keras.layers.Dropout(0.3),
    keras.layers.BatchNormalization(),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid'),         # binary classification
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss='binary_crossentropy',
    metrics=['accuracy'],
)

history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=[keras.callbacks.EarlyStopping(patience=10,
                                              restore_best_weights=True)],
)
```

For multiclass:

- Output layer: `Dense(n_classes, activation='softmax')`.
- Loss: `'sparse_categorical_crossentropy'` (integer labels) or `'categorical_crossentropy'` (one-hot labels).

For regression:

- Output layer: `Dense(1)` (linear, no activation).
- Loss: `'mse'`.

---

## Gotchas

| Bug | Symptom | Fix |
|---|---|---|
| MSE loss with sigmoid output | Non-convex loss, poor convergence | Use binary cross-entropy with sigmoid |
| Forgetting to scale features | Slow / unstable training | Standardise inputs |
| All hidden layers sigmoid in deep network | Vanishing gradient, early layers don't learn | Use ReLU + good init + batch norm |
| Dropout left on at inference | Predictions are noisy | Use `model.eval()` (PyTorch) or rely on Keras's automatic switch |
| Early stopping without `restore_best_weights` | Model returned is post-degradation | Always set `restore_best_weights=True` |
| Using `categorical_crossentropy` with integer labels | Shape mismatch error | Use `sparse_categorical_crossentropy` |
| Learning rate too high | Loss oscillates / diverges | Lower by 10× |
| Learning rate too low | Loss barely moves | Raise by 10×, or use Adam |
| Default batch size on tiny dataset | Noisy training | Smaller batch + more epochs |
| Skipping early stopping | Overfit silently after the val-loss minimum | Always include early stopping |
| `relu` everywhere, no init choice | Half the units dead from the start | Use `kernel_initializer='he_normal'` |
| Reproducibility expected without seeding everywhere | Different runs differ | Seed Python, NumPy, TF / PyTorch, and disable CUDA non-determinism |

---

## When to use what

| Need | Use | Why |
|---|---|---|
| Default deep learning loss + optimiser | Cross-entropy + Adam | Robust, well-understood |
| Hidden layer activation | ReLU | Default, fast, no saturation |
| Dying ReLU observed | Leaky ReLU / ELU / GELU | Small gradient on negative side |
| Binary output | Sigmoid + binary cross-entropy | Convex, probabilistic |
| Multiclass output | Softmax + categorical cross-entropy | Convex, probabilistic |
| Regression output | Linear + MSE | Standard |
| Regularisation, single tool | Early stopping | Free, most impactful |
| Regularisation, deep network | + Dropout 0.2-0.5 + batch norm | Standard combo |
| Modern transformer-style | LayerNorm + AdamW + GELU | Default for transformers |
| Very deep CNN / very deep network | Residual connections (ResNet) | Training stability |
| Hyperparameter tuning | Random search → Bayesian (Optuna) | Most efficient |
| Fast inference critical | Smaller model, distillation | Latency at the cost of capacity |

---

## See also

- [02_regression.md](02_regression.md) — MSE loss, linear baseline
- [03_bias_variance_and_regularization.md](03_bias_variance_and_regularization.md) — early stopping, weight decay, regularisation theory
- [04_classification.md](04_classification.md) — sigmoid, softmax, cross-entropy
- [09_model_selection.md](09_model_selection.md) — when neural networks beat tree ensembles, and when they don't
