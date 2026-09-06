"""One-shot patcher: adds the invitation UI to Organization.tsx."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "client" / "src" / "pages" / "Organization.tsx"
src = p.read_text(encoding="utf8")

# --- types ---
old_types = "type Reminder = {"
new_types = """type AvailableIndividual = {
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

type Reminder = {"""
assert old_types in src, "types anchor missing"
src = src.replace(old_types, new_types, 1)

anchor = "function OrgDashboard({ org, onLeave }: { org: OrgData; onLeave: () => void }) {"
assert anchor in src, "OrgDashboard anchor missing"

panel = """function InviteIndividualsPanel({ onDecided }: { onDecided: () => void }) {
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

"""

inbox = """function MyInvitations({ onDecided }: { onDecided: () => void }) {
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

"""

src = src.replace(anchor, panel + inbox + anchor, 1)

old_admin = """            <div className="mt-7 space-y-6">
              {isAdmin && pending.data && pending.data.length > 0 && (
                <PendingRequestsPanel requests={pending.data} onDecided={refresh} />
              )}
              <OrgDashboard org={org.data} onLeave={refresh} />
            </div>"""
new_admin = """            <div className="mt-7 space-y-6">
              {isAdmin && pending.data && pending.data.length > 0 && (
                <PendingRequestsPanel requests={pending.data} onDecided={refresh} />
              )}
              {isAdmin && <InviteIndividualsPanel onDecided={refresh} />}
              <OrgDashboard org={org.data} onLeave={refresh} />
            </div>"""
assert old_admin in src, "admin block anchor missing"
src = src.replace(old_admin, new_admin, 1)

old_join = """            <div className="mt-7 space-y-6">
              {hasPendingRequest && myRequest.data && <JoinRequestStatus request={myRequest.data} onCancel={refresh} />}"""
new_join = """            <div className="mt-7 space-y-6">
              <MyInvitations onDecided={refresh} />
              {hasPendingRequest && myRequest.data && <JoinRequestStatus request={myRequest.data} onCancel={refresh} />}"""
assert old_join in src, "join block anchor missing"
src = src.replace(old_join, new_join, 1)

p.write_text(src, encoding="utf8", newline="")
print("Organization.tsx patched")
