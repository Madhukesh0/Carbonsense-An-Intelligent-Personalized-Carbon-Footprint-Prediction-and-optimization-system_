import { useAuth } from "@/_core/hooks/useAuth";
import RepoShell from "@/components/RepoShell";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { fastApi } from "@/lib/fastapiClient";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { KeyRound, ShieldCheck, UserRound, X } from "lucide-react";
import { useState } from "react";

const roles = ["individual", "org_admin", "super_admin"] as const;

type Member = {
  id: string;
  name: string | null;
  email: string | null;
  role: (typeof roles)[number];
  country: string | null;
  isActive: boolean;
  lastSignedIn: string | null;
};

type LoginEvent = {
  id: string;
  email: string | null;
  ip: string | null;
  createdAt: string;
};

function formatLastLogin(value?: string | null): string {
  if (!value) return "Never";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Never" : `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function Modal({ title, onClose, children }: { title: string; onClose: () => void; children: React.ReactNode }) {
  return <div className="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4" onClick={onClose}><div className="cs-card w-full max-w-md p-6" onClick={(event) => event.stopPropagation()}><div className="flex items-center justify-between"><h2 className="font-bold text-foreground">{title}</h2><button onClick={onClose} className="rounded-lg p-1.5 text-muted-foreground hover:bg-muted" aria-label="Close"><X size={16} /></button></div><div className="mt-4">{children}</div></div></div>;
}

function LoginHistoryModal({ member, onClose }: { member: Member; onClose: () => void }) {
  const logins = useFastApiQuery<LoginEvent[]>(["admin", "logins", member.id], `/admin/users/${member.id}/logins`, true);
  return <Modal title={`Login history — ${member.name || member.email || member.id}`} onClose={onClose}>
    {logins.isLoading ? <p className="text-sm text-muted-foreground">Loading sign-in events...</p> : logins.error ? <p className="text-sm text-destructive">{logins.error.message}</p> : logins.data && logins.data.length ? (
      <ul className="max-h-80 space-y-2 overflow-y-auto text-sm">
        {logins.data.map((event) => <li key={event.id} className="flex items-center justify-between rounded-xl bg-muted/40 px-3 py-2 dark:bg-white/5"><span className="text-foreground">{formatLastLogin(event.createdAt)}</span><small className="text-muted-foreground">{event.ip || "IP not recorded"}</small></li>)}
      </ul>
    ) : <p className="text-sm text-muted-foreground">No sign-ins recorded yet — history starts being tracked from this deployment onward.</p>}
  </Modal>;
}

function ResetPasswordModal({ member, onClose, onDone }: { member: Member; onClose: () => void; onDone: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const reset = useMutation({
    mutationFn: () => fastApi.admin.resetPassword(member.id, { password }),
    onSuccess: () => { onDone(); onClose(); },
    onError: (err: any) => setError(err.message || "Password reset failed."),
  });
  return <Modal title={`Reset password — ${member.name || member.email || member.id}`} onClose={onClose}>
    <p className="text-sm text-muted-foreground">Set a new password for this account. All of their active sessions are revoked immediately, and the action is audit logged.</p>
    <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="New password (12+ chars, upper, lower, number)" className="mt-4 h-11 w-full rounded-xl border border-border bg-white px-3.5 text-sm outline-none focus:border-primary focus:ring-4 focus:ring-ring/30 dark:border-white/15 dark:bg-white/10" />
    {error && <p role="alert" className="mt-3 rounded-xl bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>}
    <div className="mt-4 flex justify-end gap-2">
      <button onClick={onClose} className="rounded-xl bg-muted px-4 py-2 text-sm font-bold text-secondary-foreground dark:bg-white/10">Cancel</button>
      <button disabled={reset.isPending || password.length < 12} onClick={() => reset.mutate()} className="rounded-xl bg-primary px-4 py-2 text-sm font-bold text-primary-foreground hover:bg-primary/90 disabled:opacity-60">{reset.isPending ? "Resetting..." : "Reset password"}</button>
    </div>
  </Modal>;
}

function RoleSelect({ member, disabled, onChange }: { member: Member; disabled: boolean; onChange: (role: Member["role"]) => void }) {
  return <select disabled={disabled} value={member.role} onChange={(event) => onChange(event.target.value as Member["role"])} className="w-full rounded-lg border border-border bg-white px-2 py-1.5 text-sm dark:border-white/15 dark:bg-white/10">{roles.map((role) => <option key={role} value={role}>{role.replace("_", " ")}</option>)}</select>;
}

function StatusButton({ member, disabled, onClick }: { member: Member; disabled: boolean; onClick: () => void }) {
  return <button disabled={disabled} onClick={onClick} className={`w-full rounded-lg px-3 py-2 text-xs font-bold ${member.isActive ? "bg-primary/10 text-primary dark:bg-primary/20" : "bg-muted text-secondary-foreground dark:bg-white/10 dark:text-muted-foreground"}`}>{member.isActive ? "Active — deactivate" : "Inactive — activate"}</button>;
}

export default function AdminUsers() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [loginsFor, setLoginsFor] = useState<Member | null>(null);
  const [resetFor, setResetFor] = useState<Member | null>(null);
  const [notice, setNotice] = useState("");
  const usersQuery = useFastApiQuery<Member[]>(["admin", "users"], "/admin/users", user?.role === "super_admin");
  const updateRole = useMutation({ mutationFn: ({ userId, role }: { userId: string; role: Member["role"] }) => fastApi.admin.updateRole(userId, { role }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }) });
  const updateActive = useMutation({ mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) => fastApi.admin.updateActive(userId, { is_active: isActive }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }) });
  if (user?.role !== "super_admin") return <RepoShell><main className="cs-page"><p className="rounded-2xl bg-amber-50 p-6 text-amber-900 dark:bg-amber-950 dark:text-amber-100">Super-admin access is required for user management.</p></main></RepoShell>;
  const members = (usersQuery.data || []) as Member[];
  const controls = (member: Member) => ({ disabled: member.id === user.id || updateRole.isPending || updateActive.isPending, onRoleChange: (role: Member["role"]) => updateRole.mutate({ userId: member.id, role }), onStatusChange: () => updateActive.mutate({ userId: member.id, isActive: !member.isActive }) });

  return <RepoShell><main className="cs-page"><div className="max-w-3xl"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"><ShieldCheck size={24} /></span><p className="cs-kicker mt-5 text-amber-700 dark:text-amber-300">Platform administration</p><h1 className="mt-2 text-4xl font-extrabold tracking-tight sm:text-5xl text-foreground">User management.</h1><p className="mt-4 text-base leading-7 text-muted-foreground">Roles, account status, login history, and password resets are audit logged. You cannot change or deactivate your own super-admin account from this screen.</p></div>
    {notice && <p role="status" className="mt-4 max-w-3xl rounded-xl bg-primary/8 px-4 py-3 text-sm font-semibold text-primary dark:bg-primary/20">{notice}</p>}
    {loginsFor && <LoginHistoryModal member={loginsFor} onClose={() => setLoginsFor(null)} />}
    {resetFor && <ResetPasswordModal member={resetFor} onClose={() => setResetFor(null)} onDone={() => setNotice(`Password for ${resetFor.email || resetFor.id} was reset; their sessions were revoked.`)} />}
    <section className="mt-9 md:hidden"><div className="space-y-3">{members.map((member) => { const control = controls(member); return <article key={member.id} className="cs-card p-5"><div className="flex items-start gap-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-primary/10 text-primary dark:bg-primary/20"><UserRound size={16} /></span><div className="min-w-0"><b className="block truncate text-foreground">{member.name || "Unnamed user"}</b><small className="block break-all text-muted-foreground">{member.email || "No email"} · {member.country || "No country"}</small><small className="block text-muted-foreground">Last login: {formatLastLogin(member.lastSignedIn)}</small></div></div><div className="mt-4 grid grid-cols-2 gap-3"><label className="text-xs font-bold text-muted-foreground">Role<RoleSelect member={member} disabled={control.disabled} onChange={control.onRoleChange} /></label><label className="text-xs font-bold text-muted-foreground">Account<StatusButton member={member} disabled={control.disabled} onClick={control.onStatusChange} /></label></div><div className="mt-3 grid grid-cols-2 gap-3"><button onClick={() => setLoginsFor(member)} className="rounded-lg border border-border px-3 py-2 text-xs font-bold text-secondary-foreground hover:bg-muted dark:text-muted-foreground">Login history</button><button disabled={member.id === user.id} onClick={() => setResetFor(member)} className="flex items-center justify-center gap-1.5 rounded-lg border border-border px-3 py-2 text-xs font-bold text-secondary-foreground hover:bg-muted disabled:opacity-40 dark:text-muted-foreground"><KeyRound size={12} />Reset password</button></div></article>; })}</div></section>
    <section className="cs-card mt-9 hidden overflow-hidden md:block"><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-primary/8 text-xs uppercase tracking-wider text-primary dark:bg-primary/20"><tr><th className="px-5 py-4">Member</th><th className="px-5 py-4">Last login</th><th className="px-5 py-4">Role</th><th className="px-5 py-4">Account</th><th className="px-5 py-4">Actions</th></tr></thead><tbody>{members.map((member) => { const control = controls(member); return <tr key={member.id} className="border-t border-border dark:border-white/10"><td className="px-5 py-4"><div className="flex items-center gap-3"><span className="grid h-8 w-8 place-items-center rounded-full bg-primary/10 text-primary dark:bg-primary/20"><UserRound size={15} /></span><span><b className="block">{member.name || "Unnamed user"}</b><small className="text-muted-foreground">{member.email || "No email"} · {member.country || "No country"}</small></span></div></td><td className="px-5 py-4 whitespace-nowrap text-muted-foreground">{formatLastLogin(member.lastSignedIn)}</td><td className="px-5 py-4"><RoleSelect member={member} disabled={control.disabled} onChange={control.onRoleChange} /></td><td className="px-5 py-4"><StatusButton member={member} disabled={control.disabled} onClick={control.onStatusChange} /></td><td className="px-5 py-4"><div className="flex items-center gap-2"><button onClick={() => setLoginsFor(member)} className="whitespace-nowrap rounded-lg border border-border px-3 py-2 text-xs font-bold text-secondary-foreground hover:bg-muted dark:text-muted-foreground">Logins</button><button disabled={member.id === user.id} onClick={() => setResetFor(member)} className="flex items-center gap-1.5 whitespace-nowrap rounded-lg border border-border px-3 py-2 text-xs font-bold text-secondary-foreground hover:bg-muted disabled:opacity-40 dark:text-muted-foreground"><KeyRound size={12} />Reset</button></div></td></tr>; })}</tbody></table></div></section>
  </main></RepoShell>;
}
