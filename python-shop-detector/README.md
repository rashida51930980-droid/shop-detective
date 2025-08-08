# Shop Detector AI (Local, Webcam, TTS)

A plug-and-play Python app that uses your webcam, an image captioning model, and text‑to‑speech to announce “This is a shop” when the scene looks like a shop/store.

- Camera input: OpenCV
- AI: BLIP image captioning (Hugging Face Transformers)
- TTS: Offline via pyttsx3
- Runs locally (CPU by default), no cloud keys needed
- Cooldown so it doesn’t repeat too often

## Quick Start

1) Requirements
- Python 3.9–3.12
- macOS, Windows, or Linux

2) Setup (recommended: virtual environment)

```bash
# From the repo root
cd python-shop-detector
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

3) Run

```bash
python detect_shop.py --cooldown 10 --interval 2 --camera 0
```

- Press "q" to quit the window.
- On first run, model weights are downloaded and cached.

## CLI Options

```text
--camera    Index of your webcam (default: 0)
--image     Path to an image file to analyze (skips webcam)
--cooldown  Seconds to wait after speaking before it can speak again (default: 10)
--interval  Seconds between AI inferences to keep things responsive (default: 2)
--keywords  Comma-separated overrides for shop-related keywords
--say       Custom phrase to speak (default: "This is a shop")
--threshold Minimum string match confidence (not used by captioning; reserved)
--no-window Disable preview window (headless mode)
```

Examples:
```bash
# Analyze a single image
python detect_shop.py --image path/to/photo.jpg

# Use an external USB camera and shorter cooldown
python detect_shop.py --camera 1 --cooldown 6

# Run headless (no OpenCV preview window)
python detect_shop.py --no-window

# Customize keywords
python detect_shop.py --keywords "shop,store,market,supermarket,pharmacy"
```

## How It Works
- Captures a frame at a fixed interval using OpenCV.
- Generates a caption with BLIP (Salesforce/blip-image-captioning-base).
- If the caption contains any shop-like words (shop, store, market, etc.), it speaks the phrase.
- A cooldown prevents repeating too frequently.

## Troubleshooting
- If you see camera errors, ensure no other app is using the webcam and try another `--camera` index.
- First run may be slow while downloading the model.
- CPU-only is supported by default. If you have a GPU and a proper PyTorch install, the script will detect it automatically.

## Web API (for the website UI)
Run a local API server that the React website calls:

```bash
# From python-shop-detector/
uvicorn server:app --host 127.0.0.1 --port 8000
```

- Endpoint: `POST /detect` with form-data field `file` (image)
- Response: `{ caption, is_shop, score, pun }`
- CORS is enabled for `http://localhost:5173`

Then open the web UI at `/is-this-a-shop` and upload an image.

## Uninstall
```bash
deactivate  # if you used a venv
```

## License
MIT