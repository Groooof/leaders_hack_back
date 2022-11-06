import numpy as np  
from PIL import Image

import torchvision.transforms as transforms
import torch





def preprocess(path):
    global transforms_
    img = Image.open(path)
    w, h = img.size
    img_A = img.crop((0, 0, w / 2, h))
    img_B = img.crop((w / 2, 0, w, h))

    if np.random.random() < 0.5:
        img_A = Image.fromarray(np.array(img_A)[:, ::-1, :], "RGB")
        img_B = Image.fromarray(np.array(img_B)[:, ::-1, :], "RGB")

    transforms_ = [
        transforms.Resize((img.height, img.width), Image.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ]

    img_A = transforms.Compose(transforms_)(img_A)
    img_B = transforms.Compose(transforms_)(img_B)

    return {"A": img_A, "B": img_B}


path = './test_1.jpg'
preprocessed = preprocess(path)

mod_1 = torch.load('./src/patologies_generation/utils/ai/model00.pth')

pred = mod_1.predict('Рак')


