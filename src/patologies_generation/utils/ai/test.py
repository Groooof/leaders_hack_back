import numpy as np  
from PIL import Image

import torchvision.transforms as transforms
import torch


def preprocess(path):
    img = Image.open(path)
    w, h = img.size
    img_A = img.crop((0, 0, w / 2, h))
    img_B = img.crop((w / 2, 0, w, h))

    if np.random.random() < 0.5:
        img_A = Image.fromarray(np.array(img_A)[:, ::-1, :], "RGB")
        img_B = Image.fromarray(np.array(img_B)[:, ::-1, :], "RGB")

    img_A = transforms.Compose()(img_A)
    img_B = transforms.Compose()(img_B)

    return {"A": img_A, "B": img_B}


path = './cap_1.jpg'
preprocessed = preprocess(path)

mod_1 = torch.load('./model00.pth')
pred = mod_1.predict('Рак')


