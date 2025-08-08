import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const Index = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="container py-12">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight">Shop Detector AI</h1>
        <p className="mt-4 text-lg text-muted-foreground max-w-2xl">
          Local Python app that uses your webcam and image captioning to detect shops and say “This is a shop.”
        </p>
        <div className="mt-6 flex gap-3">
          <a href="/python-shop-detector/README.md">
            <Button size="lg">Open Setup Guide</Button>
          </a>
          <a href="/python-shop-detector/detect_shop.py">
            <Button variant="secondary" size="lg">View Script</Button>
          </a>
        </div>
      </header>

      <main className="container pb-16">
        <section className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Install</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="rounded-md bg-muted p-4 overflow-x-auto text-sm">
                <code>{`cd python-shop-detector
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt`}</code>
              </pre>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Run</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="rounded-md bg-muted p-4 overflow-x-auto text-sm">
                <code>{`python detect_shop.py --cooldown 10 --interval 2 --camera 0
# Press q to quit`}</code>
              </pre>
            </CardContent>
          </Card>
        </section>
      </main>
    </div>
  );
};

export default Index;
