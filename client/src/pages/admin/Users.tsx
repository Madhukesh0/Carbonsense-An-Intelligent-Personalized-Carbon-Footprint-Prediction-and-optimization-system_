import { useAuth } from "@/_core/hooks/useAuth";
import RepoShell from "@/components/RepoShell";
import { useFastApiQuery } from "@/hooks/useFastApi";
import { fastApi } from "@/lib/fastapiClient";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ShieldCheck, UserRound } from "lucide-react";

const roles = ["individual", "org_admin", "super_admin"] as const;

type Member = {
  id: string;
  name: string | null;
  email: string | null;
  role: (typeof roles)[number];
  country: string | null;
  isActive: boolean;
};

function RoleSelect({ member, disabled, onChange }: { member: Member; disabled: boolean; onChange: (role: Member["role"]) => void }) {
  return <select disabled={disabled} value={member.role} onChange={(event) => onChange(event.target.value as Member["role"])} className="w-full rounded-lg border border-emerald-950/15 bg-white px-2 py-1.5 text-sm dark:border-white/15 dark:bg-white/10">{roles.map((role) => <option key={role} value={role}>{role.replace("_", " ")}</option>)}</select>;
}

function StatusButton({ member, disabled, onClick }: { member: Member; disabled: boolean; onClick: () => void }) {
  return <button disabled={disabled} onClick={onClick} className={`w-full rounded-lg px-3 py-2 text-xs font-bold ${member.isActive ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200" : "bg-slate-200 text-slate-700 dark:bg-white/10 dark:text-slate-300"}`}>{member.isActive ? "Active — deactivate" : "Inactive — activate"}</button>;
}

export default function AdminUsers() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const usersQuery = useFastApiQuery<Member[]>(["admin", "users"], "/admin/users", user?.role === "super_admin");
  const updateRole = useMutation({ mutationFn: ({ userId, role }: { userId: string; role: Member["role"] }) => fastApi.admin.updateRole(userId, { role }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }) });
  const updateActive = useMutation({ mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) => fastApi.admin.updateActive(userId, { is_active: isActive }), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }) });
  if (user?.role !== "super_admin") return <RepoShell><main className="cs-page"><p className="rounded-2xl bg-amber-50 p-6 text-amber-900 dark:bg-amber-950 dark:text-amber-100">Super-admin access is required for user management.</p></main></RepoShell>;
  const members = (usersQuery.data || []) as Member[];
  const controls = (member: Member) => ({ disabled: member.id === user.id || updateRole.isPending || updateActive.isPending, onRoleChange: (role: Member["role"]) => updateRole.mutate({ userId: member.id, role }), onStatusChange: () => updateActive.mutate({ userId: member.id, isActive: !member.isActive }) });

  return <RepoShell><main className="cs-page"><div className="max-w-3xl"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"><ShieldCheck size={24} /></span><p className="cs-kicker mt-5 text-amber-700 dark:text-amber-300">Platform administration</p><h1 className="mt-2 text-4xl font-extrabold tracking-tight sm:text-5xl text-slate-900 dark:text-white">User management.</h1><p className="mt-4 text-base leading-7 text-slate-600 dark:text-slate-300">Roles and account status are audit logged. You cannot change or deactivate your own super-admin account from this screen.</p></div>
    <section className="mt-9 md:hidden"><div className="space-y-3">{members.map((member) => { const control = controls(member); return <article key={member.id} className="cs-card p-5"><div className="flex items-start gap-3"><span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-950"><UserRound size={16} /></span><div className="min-w-0"><b className="block truncate text-slate-900 dark:text-white">{member.name || "Unnamed user"}</b><small className="block break-all text-slate-500">{member.email || "No email"} · {member.country || "No country"}</small></div></div><div className="mt-4 grid grid-cols-2 gap-3"><label className="text-xs font-bold text-slate-600 dark:text-slate-300">Role<RoleSelect member={member} disabled={control.disabled} onChange={control.onRoleChange} /></label><label className="text-xs font-bold text-slate-600 dark:text-slate-300">Account<StatusButton member={member} disabled={control.disabled} onClick={control.onStatusChange} /></label></div></article>; })}</div></section>
    <section className="cs-card mt-9 hidden overflow-hidden md:block"><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-emerald-50 text-xs uppercase tracking-wider text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200"><tr><th className="px-5 py-4">Member</th><th className="px-5 py-4">Role</th><th className="px-5 py-4">Account</th></tr></thead><tbody>{members.map((member) => { const control = controls(member); return <tr key={member.id} className="border-t border-emerald-950/10 dark:border-white/10"><td className="px-5 py-4"><div className="flex items-center gap-3"><span className="grid h-8 w-8 place-items-center rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-950"><UserRound size={15} /></span><span><b className="block">{member.name || "Unnamed user"}</b><small className="text-slate-500">{member.email || "No email"} · {member.country || "No country"}</small></span></div></td><td className="px-5 py-4"><RoleSelect member={member} disabled={control.disabled} onChange={control.onRoleChange} /></td><td className="px-5 py-4"><StatusButton member={member} disabled={control.disabled} onClick={control.onStatusChange} /></td></tr>; })}</tbody></table></div></section>
  </main></RepoShell>;
}
