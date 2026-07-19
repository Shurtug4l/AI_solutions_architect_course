# Requires pillow and numpy

from PIL import Image
import numpy as np

# 1) Load the cat image
img = Image.open("cat.jpg").convert("RGB")
img_np = np.array(img).astype(np.float32)

# 2) Build a pure-noise image (same shape as the cat)
noise = np.random.randint(0, 256, img_np.shape).astype(np.float32)

# Save it for reference
noise_uint8 = np.clip(noise, 0, 255).astype(np.uint8)

Image.fromarray(noise_uint8).save("noise.jpg")


# Blend the noise in, with alpha controlling how much the image is perturbed
def add_noise(img_np, noise, alpha):
    """
    alpha = 0   -> original image only
    alpha = 1   -> noise only
    values in between -> mix
    """
    out = (1 - alpha) * img_np + alpha * noise
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out


# 3) Four perturbation levels

# a) nearly invisible
alpha_invisible = 0.05    # 5% noise
img_invisible = add_noise(img_np, noise, alpha_invisible)
Image.fromarray(img_invisible).save("cat_pert_invisible.jpg")

# b) slightly visible
alpha_slight = 0.20       # 20% noise
img_slight = add_noise(img_np, noise, alpha_slight)
Image.fromarray(img_slight).save("cat_pert_slightly_visible.jpg")

# c) clearly visible
alpha_clear = 0.40        # 40% noise
img_clear = add_noise(img_np, noise, alpha_clear)
Image.fromarray(img_clear).save("cat_pert_clearly_visible.jpg")

# d) very visible
alpha_heavy = 0.60        # 60% noise
img_heavy = add_noise(img_np, noise, alpha_heavy)
Image.fromarray(img_heavy).save("cat_pert_very_visible.jpg")
