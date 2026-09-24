import { useAuth } from "@/_core/hooks/useAuth";
import RepoAuthPage from "@/components/RepoAuthPage";
import RepoShell from "@/components/RepoShell";
import PredictionResults from "@/components/predict/PredictionResults";
import { Card } from "@/components/ui/card";
import { useFastApiQuery } from "@/hooks/useFastApi";

export default function ModelPreview() {
  const { user, isAuthenticated, loading, error } = useAuth();
  const preview = useFastApiQuery<any>(
    ["fastapi", "model", "preview"],
    "/model/preview",
    isAuthenticated && user?.role === "super_admin"
  );

  if ((!loading || error) && (!isAuthenticated || user?.role !== "super_admin")) {
    return <RepoAuthPage mode="login" />;
  }
  if (preview.data) {
    return <PredictionResults result={preview.data} onReset={() => preview.refetch()} />;
  }

  return (
    <RepoShell title="Model QA">
      <main className="cs-page">
        <Card className="cs-card p-8">
          <p className="text-sm font-semibold uppercase tracking-[.16em] text-[#157f54]">
            Gradient Boosting quality assurance
          </p>
          <h1 className="mt-3 text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl">Preparing non-persistent model preview</h1>
          <p className="mt-3 text-base text-muted-foreground">
            The v2.5 artifact and feature contract are loading. No user run is being
            recorded.
          </p>
          {preview.error && <p className="mt-4 text-sm text-destructive">{preview.error.message}</p>}
        </Card>
      </main>
    </RepoShell>
  );
}
