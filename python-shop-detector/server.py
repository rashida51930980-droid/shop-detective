import io
import random
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
from transformers import pipeline

DEFAULT_KEYWORDS = [
    "shop",
    "store",
    "market",
    "supermarket",
    "mall",
    "boutique",
    "grocery",
    "bakery",
    "pharmacy",
    "bookstore",
    "butcher",
    "retail",
    "convenience",
    "outlet",
    "storefront",
    "vendor",
    "deli",
]

PUNS = [
    "Shelf-aware decision!",
    "Receipt-ing our victory!",
    "This one’s a total checkout.",
    "Aisle be back with more detections.",
    "We’re bagging this as a shop!",
]

app = FastAPI(title="Shop Detector API", version="1.0.0")

# Allow local dev origins (Vite defaults)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_captioner():
    device = 0 if torch.cuda.is_available() else -1
    print(f"[Model] Loading BLIP captioning (device={'cuda' if device == 0 else 'cpu'})…")
    return pipeline(
        task="image-to-text",
        model="Salesforce/blip-image-captioning-base",
        device=device,
    )


CAPTIONER = build_captioner()


def contains_shop_word(caption: str, keywords: List[str]) -> bool:
    low = caption.lower()
    return any(k.strip().lower() in low for k in keywords if k.strip())


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    data = await file.read()
    try:
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        return {"error": "Invalid image"}

    out = CAPTIONER(img)
    caption = out[0].get("generated_text", "") if isinstance(out, list) and out else ""
    is_shop = bool(caption) and contains_shop_word(caption, DEFAULT_KEYWORDS)
    score = random.randint(70, 99) if is_shop else random.randint(0, 40)
    pun = random.choice(PUNS) if is_shop else None

    return {
        "caption": caption,
        "is_shop": is_shop,
        "score": score,
        "pun": pun,
    }
