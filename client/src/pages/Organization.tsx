import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Card } from "@/components/ui/card";
import { fastApi } from "@/lib/fastapiClient";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Building2, CheckCircle2, Copy, Globe, Hourglass, KeyRound, LogOut, Plus, UserPlus, Users, XCircle } from "lucide-react";
import { useState } from "react";

type OrgData = {
  id: string;
  name: string;
  description: string | null;
  inviteCode: string | null;
  memberCount: number;
  members: { id: string; name: string; role: string; country: string | null }[];
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

const inputClass = "h-11 w-full rounded-xl border border-emerald-950/15 bg-white px-3.5 text-sm text-slate-900 outline-none transition focus:border-emerald-600 focus:ring-4 focus:ring-emerald-200/70 dark:border-white/15 dark:bg-white/10 dark:text-white dark:focus:border-emerald-400 dark:focus:ring-emerald-950";

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
    <div className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-6 dark:border-emerald-950 dark:bg-emerald-950/20">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"><Plus size={20} /></div>
        <div>
          <h2 className="font-bold text-slate-900 dark:text-white">Create an organization</h2>
          <p className="text-sm text-slate-500">Start a new organization and invite members via invite code.</p>
        </div>
      </div>
      <div className="mt-5 space-y-4">
        <label className="block"><span className="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-200">Organization name</span><input className={inputClass} required minLength={2} value={name} onChange={(e) => setName(e.target.value)} placeholder="Green Earth NGO" /></label>
        <label className="block"><span className="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-200">Description (optional)</span><input className={inputClass} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Our mission is to reduce emissions" /></label>
        {notice && <p className="rounded-xl bg-amber-50 px-3.5 py-3 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100">{notice}</p>}
        <button disabled={createOrg.isPending} onClick={() => createOrg.mutate({ name, description: description || undefined })} className="flex w-full items-center justify-center rounded-xl bg-emerald-700 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-800/20 transition hover:bg-emerald-600 disabled:opacity-60">
          {createOrg.isPending ? "Creating…" : "Create organization"}
        </button>
      </div>
    </div>
  );
}

function JoinRequestStatus({ request, onCancel }: { request: JoinRequestInfo; onCancel: () => void }) {
  const stateCopy: Record<JoinRequestInfo["status"], { label: string; body: string; classes: string; icon: typeof Hourglass }> = {
    pending: { label: "Waiting for approval", body: `Your request to join ${request.organizationName} was sent to the organization administrator. You will become a member once they accept it.`, classes: "border-amber-200 bg-amber-50/70 text-amber-900 dark:border-amber-950 dark:bg-amber-950/25 dark:text-amber-100", icon: Hourglass },
    approved: { label: "Membership approved", body: `You are now a member of ${request.organizationName}. Refresh or reopen this page to see your organization workspace.`, classes: "border-emerald-200 bg-emerald-50/70 text-emerald-900 dark:border-emerald-950 dark:bg-emerald-950/25 dark:text-emerald-100", icon: CheckCircle2 },
    rejected: { label: "Request declined", body: `Your request to join ${request.organizationName} was declined by the organization administrator. You can send a new request below.`, classes: "border-red-200 bg-red-50/70 text-red-900 dark:border-red-950 dark:bg-red-950/25 dark:text-red-100", icon: XCircle },
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
          <h2 className="font-bold text-slate-900 dark:text-white">Join requests</h2>
          <p className="text-sm text-slate-500">{requests.length} pending approval{requests.length !== 1 ? "s" : ""} · accepting adds the member to your organization.</p>
        </div>
      </div>
      {error && <p role="alert" className="mt-4 rounded-xl bg-red-50 px-3.5 py-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-100">{error}</p>}
      <div className="mt-4 space-y-3">
        {requests.map((r) => (
          <div key={r.id} className="flex flex-wrap items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-sm dark:bg-white/5">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">{(r.userName || "?")[0].toUpperCase()}</div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-slate-900 dark:text-white">{r.userName || "Unknown user"}</p>
              <p className="truncate text-xs text-slate-500">{r.userEmail || "no email"} · requested {new Date(r.createdAt).toLocaleString()}</p>
            </div>
            <div className="flex gap-2">
              <button disabled={busyId !== null} onClick={() => { setBusyId(r.id); decide.mutate({ id: r.id, decision: "approved" }); }} className="flex items-center gap-1.5 rounded-xl bg-emerald-700 px-3 py-2 text-xs font-bold text-white transition hover:bg-emerald-600 disabled:opacity-60"><CheckCircle2 size={13} /> Accept</button>
              <button disabled={busyId !== null} onClick={() => { setBusyId(r.id); decide.mutate({ id: r.id, decision: "rejected" }); }} className="flex items-center gap-1.5 rounded-xl bg-slate-100 px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-200 disabled:opacity-60 dark:bg-white/10 dark:text-slate-300 dark:hover:bg-white/20"><XCircle size={13} /> Decline</button>
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
          <h2 className="font-bold text-slate-900 dark:text-white">Join an organization</h2>
          <p className="text-sm text-slate-500">Enter an invite code — the administrator will review and approve your request.</p>
        </div>
      </div>
      <div className="mt-5 space-y-4">
        <label className="block"><span className="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-200">Invite code</span><input className={inputClass} required minLength={6} value={code} onChange={(e) => setCode(e.target.value)} placeholder="Paste your invite code here" /></label>
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
          <h2 className="font-bold text-slate-900 dark:text-white">Invite individuals</h2>
          <p className="text-sm text-slate-500">Unaffiliated accounts you can invite — they decide whether to accept.</p>
        </div>
      </div>
      {error && <p role="alert" className="mt-4 rounded-xl bg-red-50 px-3.5 py-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-100">{error}</p>}
      <div className="mt-4 space-y-2">
        {available.isLoading ? <p className="text-sm text-slate-500">Loading available individuals…</p>
          : rows.length ? rows.map((row) => (
            <div key={row.id} className="flex flex-wrap items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-sm dark:bg-white/5">
              <div className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-sky-100 text-sm font-bold text-sky-700 dark:bg-sky-950 dark:text-sky-300">{(row.name || row.email || "?")[0].toUpperCase()}</div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-slate-900 dark:text-white">{row.name || "Unnamed account"}</p>
                <p className="truncate text-xs text-slate-500">{row.email || "no email"}{row.country ? ` · ${row.country}` : ""}</p>
              </div>
              <button disabled={busyId !== null} onClick={() => { setBusyId(row.id); invite.mutate(row.id); }} className="flex items-center gap-1.5 rounded-xl bg-sky-700 px-3 py-2 text-xs font-bold text-white transition hover:bg-sky-600 disabled:opacity-60">
                <UserPlus size={13} /> {busyId === row.id ? "Inviting…" : "Invite"}
              </button>
            </div>
          )) : <p className="text-sm text-slate-500">No unaffiliated individuals are waiting right now.</p>}
      </div>
      {sent.data && sent.data.length > 0 && (
        <div className="mt-5 border-t border-sky-100 pt-4 dark:border-sky-950">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Invitations sent</p>
          <div className="mt-2 space-y-1.5">
            {sent.data.slice(0, 6).map((invitation) => (
              <div key={invitation.id} className="flex items-center justify-between gap-3 text-sm">
                <span className="truncate text-slate-600 dark:text-slate-300">{invitation.userEmail}</span>
                <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-bold ${invitation.status === "pending" ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200" : invitation.status === "accepted" ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200" : "bg-slate-100 text-slate-600 dark:bg-white/10 dark:text-slate-300"}`}>{invitation.status}</span>
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
    <div className="rounded-2xl border border-emerald-200 bg-emerald-50/60 p-6 dark:border-emerald-950 dark:bg-emerald-950/25">
      <div className="flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"><UserPlus size={20} /></div>
        <div>
          <h2 className="font-bold text-slate-900 dark:text-white">Organization invitations</h2>
          <p className="text-sm text-slate-500">You have {pending.length} pending invitation{pending.length !== 1 ? "s" : ""} — accept to become a member.</p>
        </div>
      </div>
      <div className="mt-4 space-y-3">
        {pending.map((invitation) => (
          <div key={invitation.id} className="flex flex-wrap items-center gap-3 rounded-xl bg-white px-4 py-3 shadow-sm dark:bg-white/5">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold text-slate-900 dark:text-white">{invitation.organizationName}</p>
              <p className="truncate text-xs text-slate-500">Invited by {invitation.invitedByName || "an administrator"} · {new Date(invitation.createdAt).toLocaleString()}</p>
            </div>
            <div className="flex gap-2">
              <button disabled={busyId !== null} onClick={() => { setBusyId(invitation.id); decide.mutate({ id: invitation.id, decision: "accepted" }); }} className="flex items-center gap-1.5 rounded-xl bg-emerald-700 px-3 py-2 text-xs font-bold text-white transition hover:bg-emerald-600 disabled:opacity-60"><CheckCircle2 size={13} /> Accept</button>
              <button disabled={busyId !== null} onClick={() => { setBusyId(invitation.id); decide.mutate({ id: invitation.id, decision: "declined" }); }} className="flex items-center gap-1.5 rounded-xl bg-slate-100 px-3 py-2 text-xs font-bold text-slate-600 transition hover:bg-slate-200 disabled:opacity-60 dark:bg-white/10 dark:text-slate-300 dark:hover:bg-white/20"><XCircle size={13} /> Decline</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function OrgDashboard({ org, onLeave }: { org: OrgData; onLeave: () => void }) {
  const [copied, setCopied] = useState(false);
  const leaveOrg = useMutation({
    mutationFn: fastApi.organization.leave,
    onSuccess: onLeave,
  });
  const copyCode = () => {
    if (org.inviteCode) { navigator.clipboard.writeText(org.inviteCode); setCopied(true); setTimeout(() => setCopied(false), 2000); }
  };
  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-gradient-to-br from-emerald-50 to-emerald-100/50 p-6 dark:from-emerald-950/50 dark:to-emerald-950/20">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Building2 size={20} className="text-emerald-700 dark:text-emerald-300" />
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">{org.name}</h2>
            </div>
            {org.description && <p className="mt-2 max-w-xl text-sm text-slate-600 dark:text-slate-300">{org.description}</p>}
            <div className="mt-3 flex flex-wrap gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/80 px-3 py-1 text-xs font-bold text-emerald-800 dark:bg-white/10 dark:text-emerald-200"><Users size={13} />{org.memberCount} member{org.memberCount !== 1 ? "s" : ""}</span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-white/80 px-3 py-1 text-xs font-bold text-emerald-800 dark:bg-white/10 dark:text-emerald-200"><Globe size={13} />{org.yourRole === "org_admin" ? "Admin" : "Member"}</span>
            </div>
          </div>
          {org.inviteCode && (
            <div className="rounded-xl bg-white/80 p-4 dark:bg-white/10">
              <p className="text-xs font-semibold text-slate-500">Invite code</p>
              <div className="mt-1.5 flex items-center gap-2">
                <code className="font-mono text-lg font-bold text-emerald-700 dark:text-emerald-300">{org.inviteCode}</code>
                <button onClick={copyCode} className="rounded-lg p-1.5 hover:bg-emerald-100 dark:hover:bg-emerald-950" title="Copy">{copied ? <CheckCircle2 size={16} className="text-emerald-600" /> : <Copy size={16} className="text-slate-400" />}</button>
              </div>
              <p className="mt-1 text-xs text-slate-500">Share with members to join</p>
            </div>
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-100 bg-white p-5 dark:border-white/10 dark:bg-white/5">
        <h3 className="flex items-center gap-2 font-bold text-slate-900 dark:text-white"><Users size={16} /> Members</h3>
        <div className="mt-4 space-y-2">
          {org.members.map((m) => (
            <div key={m.id} className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-3 dark:bg-white/5">
              <div className="flex items-center gap-3">
                <div className="grid h-8 w-8 place-items-center rounded-full bg-emerald-100 text-sm font-bold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">{(m.name || "?")[0].toUpperCase()}</div>
                <div>
                  <p className="text-sm font-semibold text-slate-900 dark:text-white">{m.name}</p>
                  <p className="text-xs text-slate-500">{m.country || "No country"} · {m.role === "org_admin" ? "Admin" : "Member"}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <button onClick={() => leaveOrg.mutate()} disabled={leaveOrg.isPending} className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-2.5 text-sm font-bold text-red-700 transition hover:bg-red-100 dark:border-red-950 dark:bg-red-950/30 dark:text-red-300 dark:hover:bg-red-950/50">
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
          <p className="cs-kicker text-emerald-700">Your organization</p>
          <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl dark:text-white">
            {org.data ? org.data.name : "Organization workspace"}
          </h1>
          <p className="mt-3 text-base leading-relaxed text-slate-500">
            {org.data
              ? "Manage your organization, invite members, and track aggregate climate action."
              : hasPendingRequest
                ? "Your join request is with the organization administrator."
                : "Create an organization, or request to join one — membership starts once an administrator approves your request."}
          </p>

          {(org.isLoading || myRequest.isLoading) ? (
            <div className="mt-6 h-48 animate-pulse rounded-2xl bg-emerald-50 dark:bg-emerald-950/40" />
          ) : org.data ? (
            <div className="mt-7 space-y-6">
              {isAdmin && pending.data && pending.data.length > 0 && (
                <PendingRequestsPanel requests={pending.data} onDecided={refresh} />
              )}
              {isAdmin && <InviteIndividualsPanel onDecided={refresh} />}
              <OrgDashboard org={org.data} onLeave={refresh} />
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

          {(org.error || myRequest.error) && <p role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{(org.error ?? myRequest.error)?.message}</p>}
        </Card>
      </main>
    </RepoShell>
  );
}
