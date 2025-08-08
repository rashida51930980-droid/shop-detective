import { useEffect, useMemo, useState } from "react";
import { Helmet } from "react-helmet-async";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

const API_URL = "http://127.0.0.1:8000/detect";

type DetectResponse = {
  caption: string;
  is_shop: boolean;
  score: number;
  pun?: string | null;
  error?: string;
};

const puns = [
  "Shelf-aware decision!",
  "Receipt-ing our victory!",
  "This one’s a total checkout.",
  "Aisle be back with more detections.",
  "We’re bagging this as a shop!",
];

const ShopLogo = () => (
  <div className="flex items-center gap-3">
    <svg width="40" height="40" viewBox="0 0 64 64" aria-hidden="true">
      <rect x="8" y="18" width="48" height="34" rx="6" fill="currentColor" className="text-primary" />
      <rect x="12" y="12" width="40" height="12" rx="4" fill="currentColor" className="text-secondary" />
      <circle cx="24" cy="36" r="3" fill="#fff" />
      <circle cx="40" cy="36" r="3" fill="#fff" />
      <path d="M22 44c4 4 16 4 20 0" stroke="#fff" strokeWidth="3" strokeLinecap="round" fill="none" />
    </svg>
    <span className="text-2xl font-bold tracking-tight">Is This a Shop?</span>
  </div>
);

export default function IsShop() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectResponse | null>(null);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    setResult(null);
    if (preview) URL.revokeObjectURL(preview);
    if (f) {
      setFile(f);
      setPreview(URL.createObjectURL(f));
    } else {
      setFile(null);
      setPreview(null);
    }
  };

  const onDetect = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(API_URL, { method: "POST", body: form });
      const data: DetectResponse = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || `Server error (${res.status})`);
      }
      setResult(data);
      if (data.is_shop) {
        toast.success("Yep. That’s a shop!");
      } else {
        toast("Not a shop.");
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || "Detection failed");
    } finally {
      setLoading(false);
    }
  };

  const statusBlock = useMemo(() => {
    if (!result) return null;
    return result.is_shop ? (
      <div className="text-center space-y-2">
        <div className="text-success text-2xl md:text-3xl font-bold">✅ “Yep. That’s a shop.”</div>
        <div className="text-5xl" aria-hidden>🏪</div>
        <p className="text-muted-foreground">{result.pun || puns[Math.floor(Math.random() * puns.length)]} — Confirmed by our elite AI shopping squad.</p>
        <div className="text-sm text-muted-foreground">Shop Score: <span className="font-semibold">{result.score}</span>/100</div>
      </div>
    ) : (
      <div className="text-center space-y-2">
        <div className="text-destructive text-2xl md:text-3xl font-bold">❌ “Nope. Not a shop.”</div>
        <p className="text-muted-foreground">AI caption didn’t match shop-like words.</p>
        <div className="text-sm text-muted-foreground">Shop Score: <span className="font-semibold">{result.score}</span>/100</div>
      </div>
    );
  }, [result]);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Helmet>
        <title>Is This a Shop? – AI Image Detector</title>
        <meta name="description" content="Upload an image and let local AI (BLIP) detect if it's a shop or storefront. Fun results with score and puns." />
        <link rel="canonical" href="/is-this-a-shop" />
      </Helmet>

      <header className="container py-10">
        <ShopLogo />
        <p className="mt-3 text-muted-foreground max-w-2xl">Upload a picture and our local AI will check if it looks like a shop, store, market, or supermarket—no cloud required.</p>
      </header>

      <main className="container pb-16">
        <section className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>1) Upload Image</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <input
                  type="file"
                  accept="image/*"
                  onChange={onFileChange}
                  className="block w-full"
                  aria-label="Upload an image to analyze"
                />
                {preview && (
                  <img
                    src={preview}
                    alt="Uploaded preview for shop detection"
                    className="w-full max-h-[360px] object-contain rounded-md border"
                    loading="lazy"
                  />)
                }
                <div>
                  <Button onClick={onDetect} disabled={!file || loading} size="lg">
                    {loading ? "Detecting…" : "Detect"}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">Make sure the Python API server is running: <code>uvicorn server:app --host 127.0.0.1 --port 8000</code></p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>2) Result</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="min-h-[200px] flex items-center justify-center">
                {statusBlock || <p className="text-muted-foreground">Result will appear here.</p>}
              </div>
              {result?.caption && (
                <p className="mt-4 text-xs text-muted-foreground">AI caption: <span className="font-medium text-foreground">“{result.caption}”</span></p>
              )}
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
}
