import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useFastApiMutation, useFastApiQuery } from "@/hooks/useFastApi";

type PrivacyPreferences = { shareAggregates: boolean };

export default function Privacy() {
  const auth = useAuth();
  const privacy = useFastApiQuery<PrivacyPreferences>(
    ["fastapi", "privacy"],
    "/privacy",
    auth.isAuthenticated
  );
  const updatePrivacy = useFastApiMutation<PrivacyPreferences, PrivacyPreferences>(
    "/privacy",
    "PATCH",
    [["fastapi", "privacy"], ["fastapi", "auth", "me"]]
  );

  if (!auth.loading && !auth.isAuthenticated) return <RepoAuthPage mode="login" />;

  const shareAggregates = privacy.data?.shareAggregates ?? false;
  const toggleSharing = () => updatePrivacy.mutate({ shareAggregates: !shareAggregates });

  return (
    <RepoShell title="Privacy">
      <main className="cs-page">
        <Card className="cs-card mx-auto max-w-3xl p-6 sm:p-8">
          <p className="cs-kicker text-emerald-700 dark:text-emerald-300">Privacy controls</p>
          <h1 className="mt-3 text-4xl font-extrabold tracking-tight sm:text-5xl text-slate-900 dark:text-white">
            Privacy and aggregate sharing
          </h1>
          <p className="mt-3 text-base leading-relaxed text-slate-500 dark:text-slate-300">
            Your individual activity, goals, recommendations, and reports remain private.
            Organization analytics include you only when you explicitly opt into aggregate sharing.
          </p>
          <div className="mt-7 flex flex-col justify-between gap-5 rounded-2xl bg-[#f6f8f7] p-5 sm:flex-row sm:items-center">
            <div>
              <p className="font-semibold text-slate-900">Share anonymized aggregates</p>
              <p className="mt-1 max-w-xl text-base leading-relaxed text-slate-500">
                Only regional averages and counts are shared; individual records, names, and member
                identities are never exposed through aggregate views.
              </p>
            </div>
            <Button
              variant={shareAggregates ? "default" : "outline"}
              className={shareAggregates ? "shrink-0 bg-[#157f54] hover:bg-[#106b47]" : "shrink-0"}
              onClick={toggleSharing}
              disabled={privacy.isLoading || updatePrivacy.isPending}
            >
              {updatePrivacy.isPending ? "Updating…" : shareAggregates ? "Sharing on" : "Sharing off"}
            </Button>
          </div>
          {(privacy.error || updatePrivacy.error) && (
            <p role="alert" className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {(privacy.error || updatePrivacy.error)?.message}
            </p>
          )}
        </Card>
      </main>
    </RepoShell>
  );
}
