import { ArrowUp } from "lucide-react";

export function BackToTop() {
  return <button type="button" aria-label="Back to top" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })} className="fixed bottom-5 right-5 rounded-full bg-emerald-700 p-3 text-white shadow-lg transition hover:bg-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-500"><ArrowUp size={18} /></button>;
}
