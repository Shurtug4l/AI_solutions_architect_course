# Adversarial noise on images

Course-provided practice material from section 3 (AI model security), translated to English.

The script blends uniform random noise into `cat.jpg` at four alpha levels (5%, 20%, 40%, 60%) and saves the perturbed copies plus the pure-noise image. It is the hands-on companion to the adversarial-examples lesson: at low alpha the perturbation is invisible to a human but can already flip the prediction of an image classifier, which is the core intuition behind evasion attacks.

Note the difference with a real adversarial attack: here the noise is random, so it degrades the image uniformly. A crafted attack (e.g. FGSM) computes the perturbation from the model's gradient and achieves misclassification with far smaller, targeted noise.

## Run

```bash
pip install pillow numpy
python modify_image.py
```

Outputs land in the working directory: `noise.jpg` and four `cat_pert_*.jpg` files.
