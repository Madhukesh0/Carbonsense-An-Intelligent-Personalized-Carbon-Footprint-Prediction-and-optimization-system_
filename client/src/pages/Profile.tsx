import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Download, ShieldAlert, Trash2, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { fastApi } from "@/lib/fastapiClient";
import { useFastApiMutation } from "@/hooks/useFastApi";

export default function RepoProfile() {
  const { user, isAuthenticated } = useAuth();
  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [region, setRegion] = useState("");
  useEffect(() => { setName(user?.name || ""); setCountry(user?.country || ""); setRegion(user?.region || ""); }, [user?.name, user?.country, user?.region]);
  const update = useFastApiMutation<any, { name: string; country?: string; region?: string }>("/profile", "PATCH", [["fastapi", "auth", "me"]]);

  const [, setLocation] = useLocation();
  const queryClient = useQueryClient();
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [confirmPassword, setConfirmPassword] = useState("");
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const deleteAccount = useMutation({
    mutationFn: () => fastApi.profile.delete({ password: confirmPassword }),
    onSuccess: async () => {
      // The server has revoked every session and cleared the auth cookies;
      // drop the cached queries and the localStorage mirror before landing
      // back on the public dashboard as a signed-out visitor.
      localStorage.removeItem("manus-runtime-user-info");
      queryClient.clear();
      setLocation("/");
    },
    onError: (error: unknown) => {
      setDeleteError(error instanceof Error ? error.message : "Account deletion failed. Please try again.");
    },
  });
  const setDeleteDialogOpen = (open: boolean) => {
    setDeleteOpen(open);
    if (!open) {
      setConfirmPassword("");
      setDeleteError(null);
    }
  };

  if (!isAuthenticated) return <RepoAuthPage mode="login" />;
  const isSuperAdmin = user?.role === "super_admin";
  return (
    <RepoShell>
      <main className="cs-page">
        <div className="max-w-3xl">
          <span className="grid h-12 w-12 place-items-center rounded-2xl bg-primary/10 text-primary dark:bg-primary/20"><UserRound size={24} /></span>
          <p className="cs-kicker mt-5 text-primary">Account profile</p>
          <h1 className="mt-2 text-4xl font-extrabold tracking-tight sm:text-5xl text-foreground">Your CarbonSense profile.</h1>
          <p className="mt-4 text-base leading-7 text-muted-foreground">Update your display and location information. Location only informs consented aggregate views; it does not expose your individual history.</p>
        </div>
        <section className="cs-card mt-9 max-w-2xl p-7 sm:p-9">
          <div className="grid gap-5 sm:grid-cols-2">
            <label className="sm:col-span-2"><span className="text-sm font-bold">Full name</span><input className="mt-2 h-11 w-full rounded-xl border border-border bg-white px-3 dark:border-white/15 dark:bg-white/10" value={name} onChange={(event) => setName(event.target.value)} /></label>
            <label><span className="text-sm font-bold">Country</span><input className="mt-2 h-11 w-full rounded-xl border border-border bg-white px-3 dark:border-white/15 dark:bg-white/10" value={country} onChange={(event) => setCountry(event.target.value)} placeholder="India" /></label>
            <label><span className="text-sm font-bold">Region / state</span><input className="mt-2 h-11 w-full rounded-xl border border-border bg-white px-3 dark:border-white/15 dark:bg-white/10" value={region} onChange={(event) => setRegion(event.target.value)} placeholder="Karnataka" /></label>
          </div>
          <button disabled={update.isPending || name.trim().length < 2} onClick={() => update.mutate({ name, country: country || undefined, region: region || undefined })} className="cs-action mt-7 inline-flex items-center rounded-xl bg-primary px-5 py-3 text-sm font-bold text-primary-foreground disabled:opacity-60"><CheckCircle2 size={16} className="mr-2" />{update.isPending ? "Saving…" : "Save profile"}</button>
          {update.isSuccess && <p className="mt-4 text-sm font-semibold text-primary">Profile saved.</p>}
          <div className="mt-8 border-t border-border pt-6 dark:border-white/10">
            <h2 className="font-bold text-foreground">Download a report</h2>
            <p className="mt-2 text-base leading-relaxed text-muted-foreground">Use the reports workspace to generate a printable, model-boundary-aware summary of your CarbonSense records.</p>
            <a href="/reports" className="mt-4 inline-flex items-center text-sm font-bold text-primary hover:underline"><Download size={15} className="mr-1.5" /> Open reports</a>
          </div>
        </section>
        {!isSuperAdmin && (
          <section className="cs-card mt-6 max-w-2xl border-destructive/30 p-7 sm:p-9">
            <span className="grid h-12 w-12 place-items-center rounded-2xl bg-destructive/10 text-destructive"><ShieldAlert size={24} /></span>
            <h2 className="mt-5 text-xl font-extrabold tracking-tight text-foreground">Danger zone</h2>
            <p className="mt-2 text-base leading-relaxed text-muted-foreground">
              Deleting your account permanently removes your profile, footprint history, activities,
              goals, recommendations, and reports. This cannot be undone.
              {user?.role === "org_admin" && " If you are the only member of your organization, the organization and its pending requests are removed too."}
            </p>
            <button onClick={() => setDeleteDialogOpen(true)} className="mt-6 inline-flex items-center rounded-xl border border-destructive/40 px-5 py-3 text-sm font-bold text-destructive hover:bg-destructive/10"><Trash2 size={16} className="mr-2" />Delete my account</button>
          </section>
        )}
        <AlertDialog open={deleteOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete your account permanently?</AlertDialogTitle>
              <AlertDialogDescription>
                Your profile, sign-in history, carbon footprint records, activities, goals,
                recommendations, and reports will be erased immediately. This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <label className="block">
              <span className="text-sm font-bold text-foreground">Confirm with your password</span>
              <input
                type="password"
                autoComplete="current-password"
                className="mt-2 h-11 w-full rounded-xl border border-border bg-white px-3 dark:border-white/15 dark:bg-white/10"
                value={confirmPassword}
                onChange={(event) => { setConfirmPassword(event.target.value); setDeleteError(null); }}
                placeholder="Your password"
              />
            </label>
            {deleteError && (
              <p role="alert" className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">{deleteError}</p>
            )}
            <AlertDialogFooter>
              <AlertDialogCancel disabled={deleteAccount.isPending}>Cancel</AlertDialogCancel>
              <AlertDialogAction
                disabled={confirmPassword.length === 0 || deleteAccount.isPending}
                onClick={(event) => { event.preventDefault(); deleteAccount.mutate(); }}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {deleteAccount.isPending ? "Deleting…" : "Delete account permanently"}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </main>
    </RepoShell>
  );
}
