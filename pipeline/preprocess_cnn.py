from PIL import Image
import torch
import torchvision.transforms as T

transform = T.Compose([
    T.Resize((256, 256)),
    T.ToTensor()
])

def load_image_tensor(path):
    img = Image.open(path).convert("RGB")
    return transform(img).unsqueeze(0)  # (1,3,256,256)

