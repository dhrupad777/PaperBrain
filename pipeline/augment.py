import os
import random
import io
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np

INPUT_DIR = Path("data/raw/synthetic/png")
OUTPUT_DIR = Path("data/raw/synthetic/png_aug")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def rotate(img):
    angle = random.uniform(-5, 5)   # small realistic rotation
    return img.rotate(angle, expand=True, fillcolor="white")


def blur(img):
    return img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 2.0)))


def noise(img):
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 15, arr.shape)  # mean, std
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def brighten(img):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(random.uniform(0.7, 1.3))


def contrast(img):
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(random.uniform(0.7, 1.4))


def compress(img):
    """simulate low-quality scan using in-memory buffer"""
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=random.randint(20, 60))
    buffer.seek(0)
    return Image.open(buffer)


def augment_image(img):
    transforms = [rotate, blur, noise, brighten, contrast, compress]
    num_transforms = random.randint(2, 4)
    
    aug_img = img.copy()
    for t in random.sample(transforms, num_transforms):
        aug_img = t(aug_img)
    
    return aug_img


def main(n_per_image=3):
    images = list(INPUT_DIR.glob("*.png"))

    print(f"Found {len(images)} base images. Augmenting each {n_per_image} times...")

    for img_path in images:
        img = Image.open(img_path).convert("RGB")
        base_name = img_path.stem

        for i in range(n_per_image):
            aug = augment_image(img)
            out_path = OUTPUT_DIR / f"{base_name}_aug_{i+1}.png"
            aug.save(out_path)
            print(f"Saved {out_path}")

    print("Augmentation complete!")


if __name__ == "__main__":
    main(n_per_image=3)

