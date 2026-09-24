import { ArrowUp } from "lucide-react";

export function BackToTop() {
  return <button type="button" aria-label="Back to top" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} className="fixed bottom-5 right-5 rounded-full bg-primary p-3 text-primary-foreground shadow-lg transition hover:bg-primary focus:outline-none focus:ring-2 focus:ring-ring/30"><ArrowUp size={18} /></button>;
}
