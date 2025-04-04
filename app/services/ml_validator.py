# app/services/ml_validator.py

import torch
from PIL import Image
from torchvision import transforms
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32",torch_dtype=torch.float16)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

model.eval()

LABELS = [
    "AI-generated digital artwork",
    "hand-drawn sketch illustration",
    "real-world photograph",
    "website screenshot",
    "offensive or inappropriate content",
    "internet meme",
    "spam or advertisement image",
    "pixel art style",
    "anime illustration",
    "3D rendered artwork",
    "company logo or branding"
]


ACCEPTED_LABELS = [
    "AI-generated digital artwork",
    "hand-drawn sketch illustration",
    "pixel art style",
    "anime illustration",
    "3D rendered artwork"
]

REJECTED_LABELS = [
    "offensive or inappropriate content",
    "spam or advertisement image",
    "website screenshot",
    "internet meme",
    "real-world photograph",
    "company logo or branding"
]


def validate_with_clip(image: Image.Image) -> dict:
    inputs = processor(text=LABELS, images=image, return_tensors="pt", padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1).squeeze().tolist()
        
        image_embedding = outputs.image_embeds.squeeze().tolist()

    top_indices = torch.topk(logits_per_image, 3).indices.squeeze().tolist()
    top_labels = [LABELS[i] for i in top_indices]
    top_scores = [round(probs[i], 4) for i in top_indices]

    is_valid = any(
        label in ACCEPTED_LABELS and score > 0.4
        for label, score in zip(top_labels, top_scores)
    )

    best_index = int(torch.argmax(logits_per_image))
    best_label = LABELS[best_index]
    best_score = round(probs[best_index], 4)

    return {
        "label": best_label,
        "score": best_score,
        "is_valid": is_valid,
        "embedding": image_embedding,
        "top_predictions": list(zip(top_labels, top_scores))

    }
