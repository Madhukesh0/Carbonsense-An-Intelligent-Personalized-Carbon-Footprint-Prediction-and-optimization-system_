import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Card } from "@/components/ui/card";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { fastApi } from "@/lib/fastapiClient";
import { useMutation, useQueryClient } from "@tanstack/react-query";

type Report = { id: string; category: string; details: string; status: "open" | "in_review" | "resolved" | "dismissed" };

export default function AdminReports() {
  const auth = useAuth();
  const allowed = auth.user?.role === "org_admin" || auth.user?.role === "super_admin";
  const queryClient = useQueryClient();
  const reports = useFastApiQuery<Report[]>(["fastapi", "reports", "admin"], "/reports/admin", Boolean(auth.isAuthenticated && allowed));
  const update = useMutation({ mutationFn: ({ id, status }: { id: string; status: Report["status"] }) => fastApi.reports.update(id, { status }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["fastapi", "reports", "admin"] }) });
  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;
  if (!auth.loading && !allowed) return <RepoShell title="Governance queue"><main className="cs-page"><Card className="cs-card mx-auto max-w-3xl p-7"><h1 className="text-2xl font-semibold">Administrator access required</h1><p className="mt-3 text-sm text-slate-500">Report review is limited to authorized organization administrators.</p></Card></main></RepoShell>;
  const setStatus = (id: string, status: Report["status"]) => update.mutate({ id, status });
  return <RepoShell title="Governance queue"><main className="cs-page"><Card className="cs-card mx-auto max-w-4xl p-6 sm:p-8"><p className="cs-kicker text-emerald-700">Authorized scope</p><h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">Governance queue</h1><p className="mt-3 text-base text-slate-500">Review reported questions and concerns within your authorized organization scope.</p><div className="mt-6 space-y-3">{reports.data?.length ? reports.data.map(report => <div key={report.id} className="rounded-2xl border border-[#dce8e3] p-4"><div className="flex flex-wrap items-center justify-between gap-3"><span className="font-semibold capitalize">{report.category.replace("_", " ")}</span><select value={report.status} onChange={event => setStatus(report.id, event.target.value as Report["status"])} className="rounded-lg border border-[#dce8e3] px-2 py-1 text-sm"><option value="open">Open</option><option value="in_review">In review</option><option value="resolved">Resolved</option><option value="dismissed">Dismissed</option></select></div><p className="mt-3 text-base leading-relaxed text-slate-600">{report.details}</p></div>) : <p className="rounded-xl bg-[#f6f8f7] p-4 text-sm text-slate-500">No reports in your queue.</p>}</div>{reports.error && <p role="alert" className="mt-5 text-sm text-red-700">{reports.error.message}</p>}</Card></main></RepoShell>;
}
