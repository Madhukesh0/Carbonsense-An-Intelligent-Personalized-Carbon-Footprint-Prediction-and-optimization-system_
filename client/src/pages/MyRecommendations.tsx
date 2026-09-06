import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { fastApi } from "@/lib/fastapiClient";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, ClipboardCheck, Send, Clock } from "lucide-react";

type CatalogItem = { key: string; title: string; description: string; category: string };
type MineItem = {
  _id: string;
  user_id: string;
  recommendation_key: string;
  status: "suggested" | "accepted" | "completed" | "verified";
  verification_status?: string;
  assigned_by_user_id?: string;
  created_at: string;
  completed_at?: string;
  self_reported_change_note?: string;
};

function stageLabel(status: string, verificationStatus?: string) {
  if (verificationStatus === "verified") return "Verified";
  if (status === "completed") return "Completed";
  if (status === "accepted") return "Accepted";
  return "Assigned to you";
}

function stageClass(status: string, verificationStatus?: string) {
  if (verificationStatus === "verified") return "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200";
  if (status === "completed") return "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200";
  if (status === "accepted") return "bg-sky-100 text-sky-800 dark:bg-sky-950 dark:text-sky-200";
  return "bg-violet-100 text-violet-800 dark:bg-violet-950 dark:text-violet-200";
}

export default function MyRecommendations() {
  const auth = useAuth();
  const queryClient = useQueryClient();

  const mine = useFastApiQuery<MineItem[]>(["fastapi", "recommendations", "mine"], "/recommendations/mine", auth.isAuthenticated);
  const catalog = useFastApiQuery<CatalogItem[]>(["fastapi", "recommendations", "catalog"], "/recommendations/catalog", auth.isAuthenticated);

  const accept = useMutation({
    mutationFn: (key: string) => fastApi.recommendations.accept({ recommendation_key: key }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["fastapi", "recommendations", "mine"] }),
  });

  const complete = useMutation({
    mutationFn: (id: string) => fastApi.recommendations.complete(id, { self_reported_change_note: null }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["fastapi", "recommendations", "mine"] }),
  });

  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;

  const catalogMap = Object.fromEntries((catalog.data || []).map((c) => [c.key, c]));
  const items = mine.data || [];

  const assigned = items.filter((i) => i.assigned_by_user_id && i.status === "suggested");
  const accepted = items.filter((i) => i.status === "accepted");
  const done = items.filter((i) => i.status === "completed" || i.verification_status === "verified");

  return (
    <RepoShell title="My Recommendations">
      <main className="cs-page">
        <Card className="cs-card mx-auto max-w-4xl p-6 sm:p-8">
          <p className="cs-kicker text-violet-700">Your action tracker</p>
          <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">
            My Recommendations
          </h1>
          <p className="mt-3 text-base leading-relaxed text-slate-500">
            See recommendations assigned by your organization and track your progress. Accept actions to commit, then mark them complete when done.
          </p>

          {items.length === 0 && !mine.isLoading && (
            <div className="mt-6 rounded-2xl bg-slate-50 p-5 text-sm text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              No recommendations yet. Your organization administrator can assign actions to you, or you can accept profile-matched suggestions from the{" "}
              <a href="/recommendations" className="font-semibold text-emerald-700 hover:underline dark:text-emerald-400">Recommendations</a> page.
            </div>
          )}

          {/* Assigned to you */}
          {assigned.length > 0 && (
            <section className="mt-7">
              <div className="flex items-center gap-2">
                <Send size={16} className="text-violet-600" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Assigned by your organization</h2>
                <span className="rounded-full bg-violet-100 px-2 py-0.5 text-xs font-bold text-violet-700 dark:bg-violet-950 dark:text-violet-300">{assigned.length}</span>
              </div>
              <div className="mt-4 grid gap-4">
                {assigned.map((item) => {
                  const cat = catalogMap[item.recommendation_key];
                  return (
                    <div key={item._id} className="rounded-2xl border border-violet-100 bg-violet-50/50 p-5 dark:border-violet-950 dark:bg-violet-950/20">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="max-w-xl">
                          <h3 className="font-bold text-slate-900 dark:text-white">{cat?.title || item.recommendation_key}</h3>
                          <p className="mt-1 text-sm leading-5 text-slate-500">{cat?.description || "An approved recommendation has been assigned to you."}</p>
                        </div>
                        <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ${stageClass(item.status, item.verification_status)}`}>
                          <Clock size={12} />{stageLabel(item.status, item.verification_status)}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">Assigned {new Date(item.created_at).toLocaleDateString()}</p>
                      <Button
                        size="sm"
                        className="mt-4 bg-violet-700 font-bold hover:bg-violet-800"
                        disabled={accept.isPending}
                        onClick={() => accept.mutate(item.recommendation_key)}
                      >
                        {accept.isPending ? "Accepting…" : "Accept recommendation"}
                      </Button>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {/* Accepted */}
          {accepted.length > 0 && (
            <section className="mt-7">
              <div className="flex items-center gap-2">
                <ClipboardCheck size={16} className="text-sky-600" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">In progress</h2>
                <span className="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-bold text-sky-700 dark:bg-sky-950 dark:text-sky-300">{accepted.length}</span>
              </div>
              <div className="mt-4 grid gap-4">
                {accepted.map((item) => {
                  const cat = catalogMap[item.recommendation_key];
                  return (
                    <div key={item._id} className="rounded-2xl border border-sky-100 bg-sky-50/50 p-5 dark:border-sky-950 dark:bg-sky-950/20">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="max-w-xl">
                          <h3 className="font-bold text-slate-900 dark:text-white">{cat?.title || item.recommendation_key}</h3>
                          <p className="mt-1 text-sm leading-5 text-slate-500">{cat?.description || "You accepted this recommendation."}</p>
                        </div>
                        <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ${stageClass(item.status, item.verification_status)}`}>
                          <ClipboardCheck size={12} />{stageLabel(item.status, item.verification_status)}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">Accepted {new Date(item.created_at).toLocaleDateString()}</p>
                      <Button
                        size="sm"
                        className="mt-4 bg-sky-700 font-bold hover:bg-sky-800"
                        disabled={complete.isPending}
                        onClick={() => complete.mutate(item._id)}
                      >
                        {complete.isPending ? "Marking complete…" : "Mark as complete"}
                      </Button>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {/* Completed / Verified */}
          {done.length > 0 && (
            <section className="mt-7">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-600" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Completed</h2>
                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-bold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">{done.length}</span>
              </div>
              <div className="mt-4 grid gap-4">
                {done.map((item) => {
                  const cat = catalogMap[item.recommendation_key];
                  return (
                    <div key={item._id} className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-5 dark:border-emerald-950 dark:bg-emerald-950/20">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div className="max-w-xl">
                          <h3 className="font-bold text-slate-900 dark:text-white">{cat?.title || item.recommendation_key}</h3>
                          {item.self_reported_change_note && (
                            <p className="mt-1 text-sm italic text-slate-500">"{item.self_reported_change_note}"</p>
                          )}
                        </div>
                        <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-bold ${stageClass(item.status, item.verification_status)}`}>
                          <CheckCircle2 size={12} />{stageLabel(item.status, item.verification_status)}
                        </span>
                      </div>
                      <p className="mt-2 text-xs text-slate-400">
                        {item.completed_at ? `Completed ${new Date(item.completed_at).toLocaleDateString()}` : `Completed ${new Date(item.created_at).toLocaleDateString()}`}
                      </p>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {(mine.error || catalog.error) && (
            <p role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">
              {(mine.error || catalog.error)?.message}
            </p>
          )}
        </Card>
      </main>
    </RepoShell>
  );
}
