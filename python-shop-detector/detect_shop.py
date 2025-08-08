import argparse
import time
import cv2
import threading
from typing import List

import numpy as np
from PIL import Image

# Transformers + BLIP captioning
import torch
from transformers import pipeline

# Offline TTS
import pyttsx3


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


class Speaker:
    """
    Simple non-blocking TTS wrapper around pyttsx3 using a background thread.
    """

    def __init__(self, rate: int = 175):
        self._engine = pyttsx3.init()
        # Tune voice rate slightly slower for clarity
        self._engine.setProperty("rate", rate)
        self._queue: List[str] = []
        self._lock = threading.Lock()
        self._stop = False
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        while not self._stop:
            text = None
            with self._lock:
                if self._queue:
                    text = self._queue.pop(0)
            if text:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as e:
                    print(f"[TTS] Error: {e}")
            else:
                time.sleep(0.05)

    def say(self, text: str):
        with self._lock:
            self._queue.append(text)

    def close(self):
        self._stop = True
        try:
            self._engine.stop()
        except Exception:
            pass


def build_captioner():
    device = 0 if torch.cuda.is_available() else -1
    print(f"[Model] Loading BLIP captioning (device={'cuda' if device == 0 else 'cpu'})…")
    captioner = pipeline(
        task="image-to-text",
        model="Salesforce/blip-image-captioning-base",
        device=device,
    )
    return captioner


def bgr_to_pil(frame_bgr: np.ndarray) -> Image.Image:
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(frame_rgb)


def contains_shop_word(caption: str, keywords: List[str]) -> bool:
    low = caption.lower()
    return any(k.strip().lower() in low for k in keywords if k.strip())


def draw_hud(frame: np.ndarray, caption: str, status: str):
    h, w = frame.shape[:2]
    # Background strip
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - 80), (w, h), (0, 0, 0), thickness=-1)
    frame[:] = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

    # Caption text
    cv2.putText(
        frame,
        f"Caption: {caption[:80]}" if caption else "Caption: …",
        (16, h - 46),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # Status text
    cv2.putText(
        frame,
        status,
        (16, h - 16),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0) if "READY" in status or "SHOP" in status else (0, 165, 255),
        2,
        cv2.LINE_AA,
    )


def main():
    parser = argparse.ArgumentParser(description="Webcam Shop Detector (Captioning + TTS)")
    parser.add_argument("--camera", type=int, default=0, help="Webcam index (default: 0)")
    parser.add_argument("--cooldown", type=float, default=10.0, help="Seconds after speaking before it can repeat (default: 10)")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between AI inferences (default: 2)")
    parser.add_argument("--keywords", type=str, default=",".join(DEFAULT_KEYWORDS), help="Comma-separated shop keywords override")
    parser.add_argument("--say", type=str, default="This is a shop", help="Phrase to speak on detection")
    parser.add_argument("--no-window", action="store_true", help="Run headless without preview window")
    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    # Initialize model + TTS
    captioner = build_captioner()
    speaker = Speaker()

    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        print(f"[Error] Could not open camera index {args.camera}.")
        return

    last_infer = 0.0
    last_spoken = 0.0
    caption_text = ""

    print("[Info] Press 'q' to quit.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[Error] Failed to read frame from camera.")
                break

            now = time.time()
            status = "READY"

            if now - last_infer >= args.interval:
                # Run captioning
                img = bgr_to_pil(frame)
                try:
                    out = captioner(img)
                    if isinstance(out, list) and out:
                        caption_text = out[0].get("generated_text", "")
                    else:
                        caption_text = ""
                except Exception as e:
                    caption_text = "<captioning error>"
                    print(f"[Model] Inference error: {e}")
                last_infer = now

                # Detection logic + cooldown
                if caption_text and contains_shop_word(caption_text, keywords):
                    if now - last_spoken >= args.cooldown:
                        speaker.say(args.say)
                        last_spoken = now
                        print(f"[Detect] SHOP detected. Caption='{caption_text}' -> Speaking: '{args.say}'")
                    else:
                        wait_left = int(args.cooldown - (now - last_spoken))
                        status = f"DETECTED (cooldown {wait_left}s)"
                else:
                    status = "READY"

            if not args.no_window:
                disp = frame.copy()
                draw_hud(disp, caption_text, status)
                cv2.imshow("Shop Detector (q to quit)", disp)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # Headless mode small sleep to avoid busy loop
                time.sleep(0.01)

    finally:
        cap.release()
        if not args.no_window:
            cv2.destroyAllWindows()
        speaker.close()


if __name__ == "__main__":
    main()
