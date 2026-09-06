import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { fastApi } from "@/lib/fastapiClient";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCircle2, Clock, Send, X } from "lucide-react";
import { useState } from "react";

type Member = { id: string; name: string; email: string; role: string; country: string | null };
type Reminder = { id: string; title: string; message: string; reminderType: string; status: string; senderName: string; createdAt: string; acknowledgedAt: string | null };

const inputClass = "h-11 w-full rounded-xl border border-emerald-950/15 bg-white px-3.5 text-sm text-slate-900 outline-none transition focus:border-emerald-600 focus:ring-4 focus:ring-emerald-200/70 dark:border-white/15 dark:bg-white/10 dark:text-white dark:focus:border-emerald-400 dark:focus:ring-emerald-950";

function AdminReminderForm({ members }: { members: Member[] }) {
  const queryClient = useQueryClient();
  const [userId, setUserId] = useState("");
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [type, setType] = useState<"nudge" | "deadline" | "achievement" | "general">("general");
  const [notice, setNotice] = useState("");

  const send = useMutation({
    mutationFn: fastApi.organization.createReminder,
    onSuccess: () => { setNotice("Reminder sent!"); setTitle(""); setMessage(""); setTimeout(() => setNotice(""), 3000); queryClient.invalidateQueries({ queryKey: ["fastapi", "reminders"] }); },
    onError: (err: any) => setNotice(err.message || "Failed to send."),
  });

  return (
    <div className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-6 dark:border-emerald-950 dark:bg-emerald-950/20">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"><Send size={18} /></div>
        <div>
          <h2 className="font-bold text-slate-900 dark:text-white">Send a reminder</h2>
          <p className="text-sm text-slate-500">Nudge a member about their climate actions.</p>
        </div>
      </div>
      <div className="mt-5 space-y-4">
        <label className="block">
          <span className="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-200">Member</span>
          <select className={inputClass} value={userId} onChange={(e) => setUserId(e.target.value)}>
            <option value="">Select a member…</option>
            {members.map((m) => <option key={m.id} value={m.id}>{m.name} ({m.email})</option>)}
          </select>
        </label>
        <label className="block">
          <span className="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-200">Type</span>
          <select className={inputClass} value={type} onChange={(e) => setType(e.target.value as any)}>
            <option value="general">General</option>
            <option value="nudge">Nudge</option>
            <option value="deadline">Deadline</option>
            <option value="achievement">Achievement</option>
          </select>
        </label>
        <label className="block">
          <span className="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-200">Title</span>
          <input className={inputClass} required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Complete your carbon survey" />
        </label>
        <label className="block">
          <span className="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-200">Message</span>
          <textarea className={`${inputClass} h-24 resize-none`} required value={message} onChange={(e) => setMessage(e.target.value)} placeholder="We noticed you haven't completed your carbon footprint survey yet. Please complete it by end of this week." />
        </label>
        {notice && <p className={`rounded-xl px-3.5 py-3 text-sm ${notice.includes("sent") ? "bg-emerald-50 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-100" : "bg-amber-50 text-amber-900 dark:bg-amber-950 dark:text-amber-100"}`}>{notice}</p>}
        <Button disabled={send.isPending || !userId || !title || !message} onClick={() => send.mutate({ user_id: userId, title, message, reminder_type: type })} className="w-full bg-emerald-700 hover:bg-emerald-600">
          {send.isPending ? "Sending…" : "Send reminder"}
        </Button>
      </div>
    </div>
  );
}

function AdminSentReminders() {
  const reminders = useFastApiQuery<Reminder[]>(["fastapi", "reminders"], "/organization/reminders", true);
  return (
    <div className="rounded-2xl border border-slate-100 bg-white p-5 dark:border-white/10 dark:bg-white/5">
      <h3 className="flex items-center gap-2 font-bold text-slate-900 dark:text-white"><Bell size={16} /> Sent reminders</h3>
      {(reminders.data || []).length === 0 ? (
        <p className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-500 dark:bg-white/5">No reminders sent yet.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {(reminders.data || []).slice(0, 10).map((r) => (
            <div key={r.id} className="flex items-start gap-3 rounded-xl bg-slate-50 p-4 dark:bg-white/5">
              <div className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg ${r.status === "acknowledged" ? "bg-emerald-100 text-emerald-700" : r.status === "dismissed" ? "bg-slate-100 text-slate-400" : "bg-amber-100 text-amber-700"}`}>
                {r.status === "acknowledged" ? <CheckCircle2 size={14} /> : r.status === "dismissed" ? <X size={14} /> : <Clock size={14} />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-900 dark:text-white">{r.title}</p>
                <p className="mt-0.5 text-xs text-slate-500">{r.reminderType} · {new Date(r.createdAt).toLocaleDateString()}</p>
              </div>
              <span className={`rounded-full px-2 py-0.5 text-xs font-bold ${r.status === "acknowledged" ? "bg-emerald-100 text-emerald-700" : r.status === "dismissed" ? "bg-slate-100 text-slate-500" : "bg-amber-100 text-amber-700"}`}>{r.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Reminders() {
  const auth = useAuth();
  const isAdmin = ["org_admin", "super_admin"].includes(auth.user?.role || "");
  const members = useFastApiQuery<Member[]>(["fastapi", "organization", "members"], "/organization/members", Boolean(auth.isAuthenticated && isAdmin));

  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;

  if (!isAdmin) {
    return (
      <RepoShell title="Reminders">
        <main className="cs-page">
          <Card className="cs-card mx-auto max-w-3xl p-7">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Admin access required</h1>
            <p className="mt-3 text-sm text-slate-500">Reminders are managed by organization administrators. You can view reminders sent to you from the Dashboard.</p>
          </Card>
        </main>
      </RepoShell>
    );
  }

  return (
    <RepoShell title="Reminders">
      <main className="cs-page">
        <Card className="cs-card mx-auto max-w-4xl p-6 sm:p-8">
          <p className="cs-kicker text-emerald-700">Organization management</p>
          <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">Reminders</h1>
          <p className="mt-3 text-base leading-relaxed text-slate-500">Send reminders to organization members to nudge them about their climate actions, goals, and recommendations.</p>

          <div className="mt-7 grid gap-6 lg:grid-cols-2">
            <AdminReminderForm members={members.data || []} />
            <AdminSentReminders />
          </div>

          {(members.error) && <p role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{members.error.message}</p>}
        </Card>
      </main>
    </RepoShell>
  );
}
