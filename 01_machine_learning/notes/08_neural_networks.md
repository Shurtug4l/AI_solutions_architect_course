# Neural Networks

## Perceptron

The perceptron is the foundational unit of neural networks. It computes a weighted sum of inputs and passes it through an activation function:

$$\hat{y} = f\left(\sum_{j=1}^{n} w_j x_j + b\right) = f(\mathbf{w}^T \mathbf{x} + b)$$

The original perceptron used a **step function** (threshold activation), making it a binary linear classifier. It can only represent linearly separable functions — the famous XOR limitation.

---

## Multi-Layer Perceptron (MLP)

A **feedforward neural network** composed of:
- **Input layer**: one node per feature
- **Hidden layers**: intermediate representations; apply a non-linear activation
- **Output layer**: one node per output (or one node per class in multiclass)

```
Input → [Dense + Activation] → ... → [Dense + Activation] → Output
```

With at least one hidden layer and a non-linear activation, an MLP can approximate any continuous function (**Universal Approximation Theorem**). In practice, depth matters: deeper networks can represent some functions exponentially more efficiently than shallow ones.

---

## Activation Functions

Non-linearity is essential: without it, any number of linear layers collapses to a single linear transformation.

### Sigmoid

$$\sigma(z) = \frac{1}{1 + e^{-z}} \in (0, 1)$$

- Output as probability; used in binary output layers
- Saturates at 0 and 1 → **vanishing gradient** when stacked in hidden layers
- Not zero-centered (outputs always positive)

### Tanh

$$\tanh(z) = \frac{e^z - e^{-z}}{e^z + e^{-z}} \in (-1, 1)$$

- Zero-centered, better than sigmoid for hidden layers
- Still saturates, still has vanishing gradient at extremes

### ReLU (Rectified Linear Unit)

$$\text{ReLU}(z) = \max(0, z)$$

- Most widely used for hidden layers
- No saturation for positive values → faster convergence
- Computationally cheap
- **Dying ReLU problem**: neurons with consistently negative pre-activations output zero permanently (zero gradient, no learning)

### Leaky ReLU / ELU / GELU

$$\text{Leaky ReLU}(z) = \max(\alpha z, z), \quad \alpha \approx 0.01$$

Fixes dying ReLU by allowing a small gradient for negative values. ELU has smooth negative part. GELU (used in transformers) is smooth everywhere.

### Softmax (output layer for multiclass)

$$\text{softmax}(z_j) = \frac{e^{z_j}}{\sum_k e^{z_k}}$$

Converts a vector of logits to a probability distribution. Used exclusively in output layers, not hidden layers.

### Summary

| Activation | Range | Use case |
|-----------|-------|----------|
| Sigmoid | (0, 1) | Binary output |
| Tanh | (−1, 1) | Hidden layers (legacy) |
| ReLU | [0, ∞) | Hidden layers (default) |
| Leaky ReLU | (−∞, ∞) | Hidden layers (when dying ReLU is a concern) |
| Softmax | (0, 1), sums to 1 | Multiclass output |
| Linear | (−∞, ∞) | Regression output |

---

## Forward Pass

Computation flows left-to-right through the network. For layer $l$:

$$\mathbf{z}^{(l)} = \mathbf{W}^{(l)} \mathbf{a}^{(l-1)} + \mathbf{b}^{(l)}$$
$$\mathbf{a}^{(l)} = f\left(\mathbf{z}^{(l)}\right)$$

where $\mathbf{a}^{(0)} = \mathbf{x}$ (input).

---

## Loss Functions

| Task | Loss | Formula |
|------|------|---------|
| Regression | MSE | $\frac{1}{m}\sum(y - \hat{y})^2$ |
| Binary classification | Binary cross-entropy | $-[y \log \hat{p} + (1-y) \log(1-\hat{p})]$ |
| Multiclass | Categorical cross-entropy | $-\sum_k y_k \log \hat{p}_k$ |

---

## Backpropagation

Backpropagation is the algorithm for computing gradients of the loss with respect to all weights efficiently using the **chain rule**.

1. **Forward pass**: compute activations at each layer, store them
2. **Compute loss** at the output
3. **Backward pass**: propagate the gradient of the loss back through each layer

For layer $l$:

$$\frac{\partial \mathcal{L}}{\partial \mathbf{W}^{(l)}} = \frac{\partial \mathcal{L}}{\partial \mathbf{z}^{(l)}} \cdot \left(\mathbf{a}^{(l-1)}\right)^T$$

This gives the gradient needed to update each weight.

**Why chain rule**: the loss depends on the output, which depends on all intermediate activations. Backprop applies the chain rule systematically from the output layer backward.

---

## Optimizers

### SGD (Stochastic Gradient Descent)

$$\mathbf{w} \leftarrow \mathbf{w} - \eta \nabla_{\mathbf{w}} \mathcal{L}$$

Simple but slow convergence; requires careful learning rate tuning.

### SGD with Momentum

Accumulates a velocity vector in the direction of persistent gradients:

$$\mathbf{v} \leftarrow \gamma \mathbf{v} + \eta \nabla_{\mathbf{w}} \mathcal{L}$$
$$\mathbf{w} \leftarrow \mathbf{w} - \mathbf{v}$$

Dampens oscillations, accelerates in consistent gradient directions. Typical $\gamma = 0.9$.

### Adam (Adaptive Moment Estimation)

Combines momentum (first moment) with per-parameter adaptive learning rates (second moment):

$$m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t$$
$$v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2$$
$$\mathbf{w} \leftarrow \mathbf{w} - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

- Default: $\beta_1 = 0.9$, $\beta_2 = 0.999$, $\epsilon = 10^{-8}$
- Robust to noisy gradients, sparse features, and varying gradient magnitudes
- **Default choice** for most deep learning tasks

### RMSProp

Divides learning rate by a running mean of recent gradient magnitudes. Predecessor to Adam. Good for recurrent networks.

---

## Training Concepts

### Epochs and Batches

- **Epoch**: one full pass through the training dataset
- **Batch size**: number of samples per gradient update
  - Smaller batches → noisier updates (regularizing), more updates per epoch, slower per epoch
  - Larger batches → more accurate gradient, fewer updates, faster per epoch, less regularizing

### Vanishing Gradient Problem

In deep networks with sigmoid/tanh activations, gradients shrink exponentially through layers during backprop (because the derivative of sigmoid is always < 0.25). Early layers receive near-zero gradients and fail to learn.

Fixes:
- Use ReLU activations (gradient is 1 for positive values, does not shrink)
- Batch Normalization (reduces internal covariate shift, stabilizes gradients)
- Residual connections (skip connections in ResNets bypass many layers)
- Careful weight initialization (He initialization for ReLU, Glorot for tanh)

---

## Regularization in Neural Networks

### Dropout

During training, randomly set a fraction $p$ of neuron activations to zero at each forward pass. This prevents co-adaptation of neurons and acts as training an ensemble of many subnetworks.

- Disabled at inference time (all neurons active, activations scaled by $1 - p$)
- Typical rates: 0.2–0.5 for hidden layers

### Batch Normalization

Normalizes the activations of each layer across the mini-batch (zero mean, unit variance), then applies learned scale and shift parameters $\gamma, \beta$:

$$\hat{z} = \frac{z - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}} \cdot \gamma + \beta$$

Benefits: stabilizes training, allows higher learning rates, reduces sensitivity to initialization, acts as mild regularization.

### L2 Regularization (Weight Decay)

Add $\lambda \sum w^2$ to the loss. In optimizers, equivalent to multiplying weights by $(1 - \lambda \eta)$ before each update. Standard regularization when dropout is insufficient.

---

## Keras Quick Reference

```python
import tensorflow as tf
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(n_features,)),
    keras.layers.Dropout(0.3),
    keras.layers.BatchNormalization(),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')   # binary
])

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    callbacks=[keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)]
)
```

For multiclass:
- Output layer: `Dense(n_classes, activation='softmax')`
- Loss: `'sparse_categorical_crossentropy'` (integer labels) or `'categorical_crossentropy'` (one-hot)
