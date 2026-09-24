import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Card } from "@/components/ui/card";
import { fastApi } from "@/lib/fastapiClient";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Building2, CheckCircle2, Copy, Eye, Globe, Hourglass, KeyRound, LogOut, Plus, UserMinus, UserPlus, Users, X, XCircle } from "lucide-react";
import { useState } from "react";

type OrgData = {
  id: string;
  name: string;
  description: string | null;
  inviteCode: string | null;
  memberCount: number;
  members: { id: string; name: string; role: string; country: string | null; lastSignedIn: string | null }[];
  yourRole: string;
};

type JoinRequestInfo = {
  id: string;
  organizationId: string;
  organizationName: string;
  status: "pending" | "approved" | "rejected";
  source: string | null;
  createdAt: string;
  decidedAt: string | null;
};

type PendingJoinRequest = {
  id: string;
  userId: string;
  userName: string | null;
  userEmail: string | null;
  organizationId: string;
  status: string;
  source: string | null;
  createdAt: string;
};

type AvailableIndividual = {
  id: string;
  name: string | null;
  email: string | null;
  country: string | null;
  alreadyInvited: boolean;
};

type OrgInvitation = {
  id: string;
  userEmail: string | null;
  status: "pending" | "accepted" | "declined";
  createdAt: string;
};

type MyInvitation = {
  id: string;
  organizationName: string;
  invitedByName: string | null;
  status: "pending" | "accepted" | "declined";
  createdAt: string;
};

type Reminder = {
  id: string;
  title: string;
  message: string;
  reminderType: string;
  status: string;
  senderName: string;
  createdAt: string;
  acknowledgedAt: string | null;
};

const inputClass = "h-11 w-full rounded-xl border border-border bg-white px-3.5 text-sm text-foreground outline-none transition focus:border-primary focus:ring-4 focus:ring-ring/30 dark:border-white/15 dark:bg-white/10 dark:focus:border-primary dark:focus:ring-ring/30";

function CreateOrgSection({ onSuccess }: { onSuccess: () => void }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [notice, setNotice] = useState("");
  const createOrg = useMutation({
    mutationFn: fastApi.organization.create,
    onSuccess: () => { setNotice(""); onSuccess(); },
    onError: (err: any) => setNotice(err.message || "Failed to create organization."),
  });
  return (
    <div className="rounded-2xl border border-border bg-primary/8 p-6 dark:border-primary/25 dark:bg-primary/20">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary dark:bg-primary/20"><Plus size={20} /></div>
        <div>
          <h2 className="font-bold text-foreground">Create an organization</h2>
          <p className="text-sm text-muted-foreground">Start a new organization and invite members via invite code.</p>
        </div>
      </div>
      <div className="mt-5 space-y-4">
        <label className="block"><span className="mb-1.5 block text-sm font-semibold text-secondary-foreground">Organization name</span><input className={inputClass} required minLength={2} value={name} onChange={(e) => setName(e.target.value)} placeholder="Green Earth NGO" /></label>
        <label className="block"><span className="mb-1.5 block text-sm font-semibold text-secondary-foreground">Description (optional)</span><input className={inputClass} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Our mission is to reduce emissions" /></label>
        {notice && <p className="rounded-xl bg-amber-50 px-3.5 py-3 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100">{notice}</p>}
        <button disabled={createOrg.isPending} onClick={() => createOrg.mutate({ name, description: description || undefined })} className="flex w-full items-center justify-center rounded-xl bg-primary px-4 py-3 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20 transition hover:bg-primary/90 disabled:opacity-60">
          {createOrg.isPending ? "Creating…" : "Create organization"}
        </button>
      </div>
    </div>
  );
}

function JoinRequestStatus({ request, onCancel }: { request: JoinRequestInfo; onCancel: () => void }) {
  const stateCopy: Record<JoinRequestInfo["status"], { label: string; body: string; classes: string; icon: typeof Hourglass }> = {
    pending: { label: "Waiting for approval", body: `Your request to join ${request.organizationName} was sent to the organization administrator. You will become a member once they accept it.`, classes: "border-amber-200 bg-amber-50/70 text-amber-900 dark:border-amber-950 dark:bg-amber-950/25 dark:text-amber-100", icon: Hourglass },
    approved: { label: "Membership approved", body: `You are now a member of ${request.organizationName}. Refresh or reopen this page to see your organization workspace.`, classes: "border-border bg-primary/8 text-primary dark:border-primary/25 dark:bg-primary/20", icon: CheckCircle2 },
    rejected: { label: "Request declined", body: `Your request to join ${request.organizationName} was declined by the organization administrator. You can send a new request below.`, classes: "border-destructive/30 bg-destructive/10 text-destructive dark:border-destructive/30 dark:bg-destructive/15 dark:text-destructive", icon: XCircle },
  };
  const state = stateCopy[request.status];
  const Icon = state.icon;
  return (
    <div className={`rounded-2xl border p-6 ${state.classes}`}>
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-white/70 dark:bg-white/10"><Icon size={20} /></div>
        <div>
          <h2 className="font-bold">{state.label}</h2>
          <p className="text-sm opacity-80">Requested {new Date(request.createdAt).toLocaleString()}{request.decidedAt ? ` · Decided ${new Date(request.decidedAt).toLocaleString()}` : ""}</p>
        </div>
      </div>
      <p className="mt-4 text-sm leading-6">{state.body}</p>
      {request.status === "pending" && <p className="mt-2 text-xs font-semibold uppercase tracking-wider opacity-70">You will see a confirmation here once the administrator decides.</p>}
      {request.status !== "pending" && <button onClick={onCancel} className="mt-4 rounded-xl bg-white/70 px-4 py-2 text-sm font-bold shadow-sm transition hover:bg-white dark:bg-white/10 dark:hover:bg-white/20">Back to join options</button>}
    </div>
  );
}

function PendingRequestsPanel({ requests, onDecided }: { requests: PendingJoinRequest[]; onDecided: () => void }) {
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const decide = useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: "approved" | "rejected" }) => fastApi.organization.decideJoinRequest(id, decision),
    onSettled: () => setBusyId(null),
    onError: (err: any) => setError(err.message || "Failed to record the decision."),
    onSuccess: () => { setError(""); onDecided(); },
  });
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50/50 p-6 dark:border-amber-950 dark:bg-amber-950/20">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"><UserPlus size={20} /></div>
        <div>
          <h2 className="font-bold text-foreground">Join requests</h2>
          <p className="text-sm text-muted-foreground">{requests.length} pending approval{requests.length !== 1 ? "s" : ""} · accepting adds the member to your organization.</p>
        </div>
      </div>
      {error && <p role="alert" className="mt-4 rounded-xl bg-destructive/10 px-3.5 py-3 text-sm text-destructive dark:bg-destructive/15 dark:text-destructive">{error}</p>}
      <div className="mt-4 space-y-3">
        {requests.map((r) => (
          <div key={r.id} className="flex flex-wrap items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-sm dark:bg-white/5">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-sm font-bold text-primary dark:bg-primary/20">{(r.userName || "?")[0].toUpperCase()}</div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-foreground">{r.userName || "Unknown user"}</p>
              <p className="truncate text-xs text-muted-foreground">{r.userEmail || "no email"} · requested {new Date(r.createdAt).toLocaleString()}</p>
            </div>
            <div className="flex gap-2">
              <button disabled={busyId !== null} onClick={() => { setBusyId(r.id); decide.mutate({ id: r.id, decision: "approved" }); }} className="flex items-center gap-1.5 rounded-xl bg-primary px-3 py-2 text-xs font-bold text-primary-foreground transition hover:bg-primary/90 disabled:opacity-60"><CheckCircle2 size={13} /> Accept</button>
              <button disabled={busyId !== null} onClick={() => { setBusyId(r.id); decide.mutate({ id: r.id, decision: "rejected" }); }} className="flex items-center gap-1.5 rounded-xl bg-muted px-3 py-2 text-xs font-bold text-muted-foreground transition hover:bg-muted disabled:opacity-60 dark:bg-white/10 dark:hover:bg-white/20"><XCircle size={13} /> Decline</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function JoinOrgSection({ onSuccess }: { onSuccess: () => void }) {
  const [code, setCode] = useState("");
  const [notice, setNotice] = useState("");
  const joinOrg = useMutation({
    mutationFn: fastApi.organization.join,
    onSuccess: () => { setNotice(""); onSuccess(); },
    onError: (err: any) => setNotice(err.message || "Failed to join."),
  });
  return (
    <div className="rounded-2xl border border-sky-100 bg-sky-50/50 p-6 dark:border-sky-950 dark:bg-sky-950/20">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300"><KeyRound size={20} /></div>
        <div>
          <h2 className="font-bold text-foreground">Join an organization</h2>
          <p className="text-sm text-muted-foreground">Enter an invite code — the administrator will review and approve your request.</p>
        </div>
      </div>
      <div className="mt-5 space-y-4">
        <label className="block"><span className="mb-1.5 block text-sm font-semibold text-secondary-foreground">Invite code</span><input className={inputClass} required minLength={6} value={code} onChange={(e) => setCode(e.target.value)} placeholder="Paste your invite code here" /></label>
        {notice && <p className="rounded-xl bg-amber-50 px-3.5 py-3 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100">{notice}</p>}
        <button disabled={joinOrg.isPending} onClick={() => joinOrg.mutate({ invite_code: code })} className="flex w-full items-center justify-center rounded-xl bg-sky-700 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-sky-800/20 transition hover:bg-sky-600 disabled:opacity-60">
          {joinOrg.isPending ? "Sending request…" : "Request to join"}
        </button>
      </div>
    </div>
  );
}

function InviteIndividualsPanel({ onDecided }: { onDecided: () => void }) {
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const available = useFastApiQuery<AvailableIndividual[]>(
    ["fastapi", "organization", "available-individuals"],
    "/organization/available-individuals",
    true,
  );
  const sent = useFastApiQuery<OrgInvitation[]>(
    ["fastapi", "organization", "invitations"],
    "/organization/invitations",
    true,
  );
  const invite = useMutation({
    mutationFn: (userId: string) => fastApi.organization.inviteIndividual({ user_id: userId }),
    onSettled: () => setBusyId(null),
    onError: (err: any) => setError(err.message || "Failed to send the invitation."),
    onSuccess: () => { setError(""); onDecided(); },
  });
  const rows = (available.data ?? []).filter((row) => !row.alreadyInvited);
  return (
    <div className="rounded-2xl border border-sky-200 bg-sky-50/50 p-6 dark:border-sky-950 dark:bg-sky-950/20">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300"><UserPlus size={20} /></div>
        <div>
          <h2 className="font-bold text-foreground">Invite individuals</h2>
          <p className="text-sm text-muted-foreground">Unaffiliated accounts you can invite — they decide whether to accept.</p>
        </div>
      </div>
      {error && <p role="alert" className="mt-4 rounded-xl bg-destructive/10 px-3.5 py-3 text-sm text-destructive dark:bg-destructive/15 dark:text-destructive">{error}</p>}
      <div className="mt-4 space-y-2">
        {available.isLoading ? <p className="text-sm text-muted-foreground">Loading available individuals…</p>
          : rows.length ? rows.map((row) => (
            <div key={row.id} className="flex flex-wrap items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-sm dark:bg-white/5">
              <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-sky-100 text-sm font-bold text-sky-700 dark:bg-sky-950 dark:text-sky-300">{(row.name || row.email || "?")[0].toUpperCase()}</div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-foreground">{row.name || "Unnamed account"}</p>
                <p className="truncate text-xs text-muted-foreground">{row.email || "no email"}{row.country ? ` · ${row.country}` : ""}</p>
              </div>
              <button disabled={busyId !== null} onClick={() => { setBusyId(row.id); invite.mutate(row.id); }} className="flex items-center gap-1.5 rounded-xl bg-sky-700 px-3 py-2 text-xs font-bold text-white transition hover:bg-sky-600 disabled:opacity-60">
                <UserPlus size={13} /> {busyId === row.id ? "Inviting…" : "Invite"}
              </button>
            </div>
          )) : <p className="text-sm text-muted-foreground">No unaffiliated individuals are waiting right now.</p>}
      </div>
      {sent.data && sent.data.length > 0 && (
        <div className="mt-5 border-t border-sky-100 pt-4 dark:border-sky-950">
          <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Invitations sent</p>
          <div className="mt-2 space-y-1.5">
            {sent.data.slice(0, 6).map((invitation) => (
              <div key={invitation.id} className="flex items-center justify-between gap-3 text-sm">
                <span className="truncate text-muted-foreground">{invitation.userEmail}</span>
                <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-bold ${invitation.status === "pending" ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200" : invitation.status === "accepted" ? "bg-primary/10 text-primary dark:bg-primary/20" : "bg-muted text-muted-foreground dark:bg-white/10"}`}>{invitation.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MyInvitations({ onDecided }: { onDecided: () => void }) {
  const [busyId, setBusyId] = useState<string | null>(null);
  const invitations = useFastApiQuery<MyInvitation[]>(
    ["fastapi", "organization", "my-invitations"],
    "/organization/invitations/mine",
    true,
  );
  const decide = useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: "accepted" | "declined" }) => fastApi.organization.decideInvitation(id, decision),
    onSettled: () => setBusyId(null),
    onSuccess: onDecided,
  });
  const pending = (invitations.data ?? []).filter((invitation) => invitation.status === "pending");
  if (invitations.isLoading || pending.length === 0) return null;
  return (
    <div className="rounded-2xl border border-border bg-primary/8 p-6 dark:border-primary/25 dark:bg-primary/20">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary/10 text-primary dark:bg-primary/20"><UserPlus size={20} /></div>
        <div>
          <h2 className="font-bold text-foreground">Organization invitations</h2>
          <p className="text-sm text-muted-foreground">You have {pending.length} pending invitation{pending.length !== 1 ? "s" : ""} — accept to become a member.</p>
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {pending.map((invitation) => (
          <div key={invitation.id} className="flex flex-wrap items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-sm dark:bg-white/5">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-foreground">{invitation.organizationName}</p>
              <p className="truncate text-xs text-muted-foreground">Invited by {invitation.invitedByName || "an administrator"} · {new Date(invitation.createdAt).toLocaleString()}</p>
            </div>
            <div className="flex gap-2">
              <button disabled={busyId !== null} onClick={() => { setBusyId(invitation.id); decide.mutate({ id: invitation.id, decision: "accepted" }); }} className="flex items-center gap-1.5 rounded-xl bg-primary px-3 py-2 text-xs font-bold text-primary-foreground transition hover:bg-primary/90 disabled:opacity-60"><CheckCircle2 size={13} /> Accept</button>
              <button disabled={busyId !== null} onClick={() => { setBusyId(invitation.id); decide.mutate({ id: invitation.id, decision: "declined" }); }} className="flex items-center gap-1.5 rounded-xl bg-muted px-3 py-2 text-xs font-bold text-muted-foreground transition hover:bg-muted disabled:opacity-60 dark:bg-white/10 dark:hover:bg-white/20"><XCircle size={13} /> Decline</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function formatLastSignedIn(value: string | null): string {
  if (!value) return "Never signed in";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Never signed in";
  return `Last signed in ${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

type MemberDetail = {
  id: string;
  name: string | null;
  email: string | null;
  role: string;
  country: string | null;
  lastSignedIn: string | null;
  createdAt: string | null;
  runs: { id: string; predictedKg: number | null; region: string | null; createdAt: string | null }[];
  activeGoal: { baselineKg: number; targetKg: number; deadline: string | null; createdAt: string | null } | null;
  activities: { id: string; activityDate: string | null; category: string | null; quantity: number | null; unit: string | null; co2Kg: number | null; notes: string | null }[];
  recommendations: { assigned: number; accepted: number; completed: number; verified: number };
};

function fmtDate(value: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "—" : date.toLocaleDateString();
}

function MemberDetailModal({ memberId, memberName, onClose }: { memberId: string; memberName: string | null; onClose: () => void }) {
  const detail = useFastApiQuery<MemberDetail | null>(["fastapi", "admin", "member-detail", memberId], `/admin/users/${memberId}/detail`, true);
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4" onClick={onClose}>
      <div className="cs-card max-h-[85vh] w-full max-w-lg overflow-y-auto p-6" onClick={(event) => event.stopPropagation()}>
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-foreground">Member record — {memberName || memberId}</h3>
          <button onClick={onClose} className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted" aria-label="Close"><X size={16} /></button>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">This view is recorded in the governance audit log.</p>
        {detail.isLoading ? <p className="mt-6 text-sm text-muted-foreground">Loading member records...</p> : detail.error ? <p className="mt-6 text-sm text-destructive">{detail.error.message}</p> : detail.data && (
          <div className="mt-5 space-y-5 text-sm">
            <div className="rounded-xl bg-muted/40 px-4 py-3 dark:bg-white/5">
              <p className="font-semibold text-foreground">{detail.data.email || "No email"}</p>
              <p className="mt-1 text-xs text-muted-foreground">{detail.data.country || "No country"} · {detail.data.role} · {formatLastSignedIn(detail.data.lastSignedIn)}</p>
            </div>
            <div>
              <p className="cs-data-label">Footprint runs ({detail.data.runs.length})</p>
              {detail.data.runs.length ? <ul className="mt-2 space-y-1">{detail.data.runs.map((run) => <li key={run.id} className="flex justify-between rounded-lg bg-muted/40 px-3 py-1.5 text-xs dark:bg-white/5"><span>{fmtDate(run.createdAt)} · {run.region || "region n/a"}</span><b className="text-foreground">{run.predictedKg?.toLocaleString()} kg</b></li>)}</ul> : <p className="mt-1 text-xs text-muted-foreground">No saved predictions.</p>}
            </div>
            <div>
              <p className="cs-data-label">Active goal</p>
              {detail.data.activeGoal ? <p className="mt-1 text-xs text-muted-foreground">Reduce from {detail.data.activeGoal.baselineKg.toLocaleString()} kg to {detail.data.activeGoal.targetKg.toLocaleString()} kg by {fmtDate(detail.data.activeGoal.deadline)}.</p> : <p className="mt-1 text-xs text-muted-foreground">No active goal.</p>}
            </div>
            <div>
              <p className="cs-data-label">Recent activity ({detail.data.activities.length})</p>
              {detail.data.activities.length ? <ul className="mt-2 space-y-1">{detail.data.activities.map((a) => <li key={a.id} className="flex justify-between rounded-lg bg-muted/40 px-3 py-1.5 text-xs dark:bg-white/5"><span>{fmtDate(a.activityDate)} · {a.category} · {a.quantity} {a.unit}</span><b className="text-foreground">{a.co2Kg} kg</b></li>)}</ul> : <p className="mt-1 text-xs text-muted-foreground">No ledger entries.</p>}
            </div>
            <div>
              <p className="cs-data-label">Recommendations</p>
              <p className="mt-1 text-xs text-muted-foreground">{detail.data.recommendations.assigned} assigned · {detail.data.recommendations.accepted} accepted · {detail.data.recommendations.completed} self-reported · {detail.data.recommendations.verified} verified</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function OrgDashboard({ org, currentUserId, isAdmin, isSuperAdmin, onLeave }: { org: OrgData; currentUserId: string; isAdmin: boolean; isSuperAdmin: boolean; onLeave: () => void }) {
  const [copied, setCopied] = useState(false);
  const [removeError, setRemoveError] = useState("");
  const [detailFor, setDetailFor] = useState<OrgData["members"][number] | null>(null);
  const leaveOrg = useMutation({
    mutationFn: fastApi.organization.leave,
    onSuccess: onLeave,
  });
  const removeMember = useMutation({
    mutationFn: fastApi.organization.removeMember,
    onSuccess: () => { setRemoveError(""); onLeave(); },
    onError: (err: any) => setRemoveError(err.message || "Failed to remove the member."),
  });
  const canRemove = (m: OrgData["members"][number]) =>
    isAdmin && m.id !== currentUserId && (m.role !== "org_admin" || isSuperAdmin);
  const copyCode = () => {
    if (org.inviteCode) { navigator.clipboard.writeText(org.inviteCode); setCopied(true); setTimeout(() => setCopied(false), 2000); }
  };
  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-gradient-to-br from-emerald-50 to-emerald-100/50 p-6 dark:from-emerald-950/50 dark:to-emerald-950/20">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Building2 size={20} className="text-primary" />
              <h2 className="text-xl font-bold text-foreground">{org.name}</h2>
            </div>
            {org.description && <p className="mt-2 max-w-xl text-sm text-muted-foreground">{org.description}</p>}
            <div className="mt-3 flex flex-wrap gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/80 px-3 py-1 text-xs font-bold text-primary dark:bg-white/10"><Users size={13} />{org.memberCount} member{org.memberCount !== 1 ? "s" : ""}</span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/80 px-3 py-1 text-xs font-bold text-primary dark:bg-white/10"><Globe size={13} />{org.yourRole === "org_admin" ? "Admin" : "Member"}</span>
            </div>
          </div>
          {org.inviteCode && (
            <div className="rounded-xl bg-white/80 p-4 dark:bg-white/10">
              <p className="text-xs font-semibold text-muted-foreground">Invite code</p>
              <div className="mt-1.5 flex items-center gap-2">
                <code className="font-mono text-lg font-bold text-primary">{org.inviteCode}</code>
                <button onClick={copyCode} className="rounded-lg p-1.5 hover:bg-primary/10 dark:hover:bg-primary/20" title="Copy">{copied ? <CheckCircle2 size={16} className="text-primary" /> : <Copy size={16} className="text-muted-foreground" />}</button>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">Share with members to join</p>
            </div>
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-white p-5 dark:border-white/10 dark:bg-white/5">
        <h3 className="flex items-center gap-2 font-bold text-foreground"><Users size={16} /> Members</h3>
        {removeError && <p role="alert" className="mt-2 rounded-xl bg-destructive/10 px-3 py-2 text-xs text-destructive dark:bg-destructive/15 dark:text-destructive">{removeError}</p>}
        <div className="mt-4 space-y-2">
          {org.members.map((m) => (
            <div key={m.id} className="flex items-center justify-between rounded-xl bg-muted/40 px-4 py-3 dark:bg-white/5">
              <div className="flex items-center gap-3">
                <div className="grid h-8 w-8 place-items-center rounded-full bg-primary/10 text-sm font-bold text-primary dark:bg-primary/20">{(m.name || "?")[0].toUpperCase()}</div>
                <div>
                  <p className="text-sm font-semibold text-foreground">{m.name}</p>
                  <p className="text-xs text-muted-foreground">{m.country || "No country"} · {m.role === "org_admin" ? "Admin" : "Member"} · {formatLastSignedIn(m.lastSignedIn)}</p>
                </div>
              </div>
              {isAdmin && (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setDetailFor(m)}
                    className="flex items-center gap-1.5 rounded-lg border border-border px-2.5 py-1.5 text-xs font-bold text-secondary-foreground transition hover:bg-muted dark:text-muted-foreground"
                    title="View individual record (audit logged)"
                  >
                    <Eye size={13} />Details
                  </button>
                  {canRemove(m) && (
                    <button
                      onClick={() => { if (window.confirm(`Remove ${m.name || "this member"} from the organization?`)) removeMember.mutate(m.id); }}
                      disabled={removeMember.isPending}
                      className="flex items-center gap-1.5 rounded-lg border border-destructive/30 bg-destructive/10 px-2.5 py-1.5 text-xs font-bold text-destructive transition hover:bg-destructive/15 disabled:opacity-60 dark:border-destructive/30 dark:bg-destructive/15 dark:text-destructive dark:hover:bg-destructive/15"
                      title="Remove from organization"
                    >
                      <UserMinus size={13} />{removeMember.isPending ? "Removing..." : "Remove"}
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {detailFor && <MemberDetailModal memberId={detailFor.id} memberName={detailFor.name} onClose={() => setDetailFor(null)} />}

      <button onClick={() => leaveOrg.mutate()} disabled={leaveOrg.isPending} className="flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-2.5 text-sm font-bold text-destructive transition hover:bg-destructive/15 dark:border-destructive/30 dark:bg-destructive/15 dark:text-destructive dark:hover:bg-destructive/15">
        <LogOut size={16} />{leaveOrg.isPending ? "Leaving…" : "Leave organization"}
      </button>
    </div>
  );
}

export default function Organization() {
  const auth = useAuth();
  const queryClient = useQueryClient();
  const org = useFastApiQuery<OrgData | null>(["fastapi", "organization", "me"], "/organization/me", auth.isAuthenticated);
  const myRequest = useFastApiQuery<JoinRequestInfo | null>(["fastapi", "organization", "join-request", "mine"], "/organization/join-requests/mine", auth.isAuthenticated);
  const isAdmin = ["org_admin", "super_admin"].includes(auth.user?.role || "");
  const pending = useFastApiQuery<PendingJoinRequest[]>(["fastapi", "organization", "join-requests"], "/organization/join-requests", auth.isAuthenticated && isAdmin);
  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["fastapi", "organization"] });
    queryClient.invalidateQueries({ queryKey: ["auth"] });
  };

  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;

  const hasPendingRequest = !org.data && myRequest.data?.status === "pending";
  const showJoinOptions = !org.data && (!myRequest.data || myRequest.data.status === "rejected");

  return (
    <RepoShell title="Organization">
      <main className="cs-page">
        <Card className="cs-card mx-auto max-w-4xl p-6 sm:p-8">
          <p className="cs-kicker text-primary">Your organization</p>
          <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">
            {org.data ? org.data.name : "Organization workspace"}
          </h1>
          <p className="mt-3 text-base leading-relaxed text-muted-foreground">
            {org.data
              ? "Manage your organization, invite members, and track aggregate climate action."
              : hasPendingRequest
                ? "Your join request is with the organization administrator."
                : "Create an organization, or request to join one — membership starts once an administrator approves your request."}
          </p>

          {(org.isLoading || myRequest.isLoading) ? (
            <div className="mt-6 h-48 animate-pulse rounded-2xl bg-primary/8 dark:bg-primary/20/40" />
          ) : org.data ? (
            <div className="mt-7 space-y-6">
              {isAdmin && pending.data && pending.data.length > 0 && (
                <PendingRequestsPanel requests={pending.data} onDecided={refresh} />
              )}
              {isAdmin && <InviteIndividualsPanel onDecided={refresh} />}
              <OrgDashboard
                org={org.data}
                currentUserId={auth.user?.id ?? ""}
                isAdmin={isAdmin}
                isSuperAdmin={auth.user?.role === "super_admin"}
                onLeave={refresh}
              />
            </div>
          ) : (
            <div className="mt-7 space-y-6">
              <MyInvitations onDecided={refresh} />
              {hasPendingRequest && myRequest.data && <JoinRequestStatus request={myRequest.data} onCancel={refresh} />}
              {showJoinOptions && (
                <div className="grid gap-6 lg:grid-cols-2">
                  <CreateOrgSection onSuccess={refresh} />
                  <JoinOrgSection onSuccess={refresh} />
                </div>
              )}
            </div>
          )}

          {(org.error || myRequest.error) && <p role="alert" className="mt-5 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">{(org.error ?? myRequest.error)?.message}</p>}
        </Card>
      </main>
    </RepoShell>
  );
}
