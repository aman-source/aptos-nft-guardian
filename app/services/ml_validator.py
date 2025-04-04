# app/services/ml_validator.py

import torch
from PIL import Image
from torchvision import transforms
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

model.eval()

LABELS = [
    "AI-generated artwork",
    "hand-drawn illustration",
    "real photograph",
    "screenshot",
    "offensive content",
    "meme",
    "spam image",
]

ACCEPTED_LABELS = [
    "AI-generated art",
    "hand-drawn illustration",
    "3D artwork",
    "pixel art",
    "digital illustration",
    "anime art",
]

REJECTED_LABELS = [
    "offensive content",
    "spam image",
    "screenshot",
    "meme",
    "photograph",
    "logo",
]

def validate_with_clip(image: Image.Image) -> dict:
    inputs = processor(text=LABELS, images=image, return_tensors="pt", padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).squeeze().tolist()

    best_index = int(torch.argmax(logits_per_image))
    best_label = LABELS[best_index]
    best_score = round(probs[best_index], 4)

    is_valid = (
        best_label in ACCEPTED_LABELS
        and best_score > 0.4  
    )

    return {
        "label": best_label,
        "score": best_score,
        "is_valid": is_valid
    }
