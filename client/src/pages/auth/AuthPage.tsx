import { useTheme } from "@/contexts/ThemeContext";
import { fastApi } from "@/lib/fastapiClient";
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  Database,
  HardDrive,
  KeyRound,
  Leaf,
  LockKeyhole,
  Mail,
  Moon,
  ShieldCheck,
  Sun,
  UserRound,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useState } from "react";
import { Link, useLocation } from "wouter";

type AuthMode = "login" | "register" | "forgot";

type OrganizationOption = {
  id: string;
  name: string;
  description: string | null;
  inviteCode: string | null;
  memberCount: number;
  createdAt: string | null;
};

const countries = [
  "Australia",
  "Brazil",
  "Canada",
  "Germany",
  "India",
  "Japan",
  "Kenya",
  "United Kingdom",
  "United States",
];

function AuthBrand() {
  return (
    <Link href="/" className="inline-flex items-center gap-3">
      <span className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-800 text-lg font-extrabold text-white shadow-lg shadow-primary/20">
        C
      </span>
      <span>
        <span className="block text-xl font-bold tracking-[-0.06em] text-foreground">
          CarbonSense
        </span>
        <span className="block text-[9px] font-bold tracking-[0.16em] text-primary">
          INTELLIGENT CLIMATE AI
        </span>
      </span>
    </Link>
  );
}

function Field({
  label,
  children,
  right,
}: {
  label: string;
  children: React.ReactNode;
  right?: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-2 flex items-center justify-between text-sm font-semibold text-secondary-foreground">
        <span>{label}</span>
        {right}
      </span>
      {children}
    </label>
  );
}

function StorageBoundary() {
  return (
    <details className="cs-card mt-5 overflow-hidden p-0 text-left">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 text-sm font-bold text-foreground marker:content-none">
        <span className="inline-flex items-center gap-2">
          <ShieldCheck
            size={17}
            className="text-primary"
          />
          Where your sign-up and sign-in data is stored
        </span>
        <span className="font-mono text-[0.62rem] font-medium tracking-[0.11em] text-primary">
          VIEW DETAILS
        </span>
      </summary>
      <div className="grid gap-3 border-t border-border bg-primary/8 p-4 text-xs leading-5 text-muted-foreground dark:border-white/10 dark:bg-white/5">
        <article className="rounded-xl bg-white/80 p-4 dark:bg-white/5">
          <p className="flex items-center gap-2 font-bold text-foreground">
            <Database
              size={15}
              className="text-primary"
            />
            MongoDB Atlas — native account credentials
          </p>
          <p className="mt-2">
            Native email/password accounts store your email, profile fields,
            timestamps, and an <b>Argon2 password hash</b> in the Atlas{" "}
            <code>carbonsense_fastapi.users</code> collection. Your plaintext
            password is never stored.
          </p>
        </article>
        <article className="rounded-xl bg-white/80 p-4 dark:bg-white/5">
          <p className="flex items-center gap-2 font-bold text-foreground">
            <HardDrive
              size={15}
              className="text-primary"
            />
            CarbonSense MongoDB workspace
          </p>
          <p className="mt-2">
            Your name, email, country, role, and the CarbonSense records you
            create—such as estimates, activity, goals, and governance
            history—are stored in the same protected application database.
            Passwords are represented only by their Argon2 hash.
          </p>
        </article>
        <article className="rounded-xl bg-white/80 p-4 dark:bg-white/5">
          <p className="flex items-center gap-2 font-bold text-foreground">
            <ShieldCheck
              size={15}
              className="text-primary"
            />
            Your browser — session only
          </p>
          <p className="mt-2">
            The form holds email and password only while this page is open and
            does not persist credentials in browser local storage or session
            storage. After sign-in, the browser receives an{" "}
            <b>HTTP-only session cookie</b>; the app cannot read it with page
            scripts. Theme preference may be stored locally, never credentials.
          </p>
        </article>
        <article className="rounded-xl border border-border bg-primary/8 p-4 text-primary dark:border-primary/25 dark:bg-primary/20">
          <p className="font-bold">Native CarbonSense account</p>
          <p className="mt-2">
            This clean account flow uses only the email and password you create
            here. It issues short-lived HTTP-only JWT session cookies and a
            separate CSRF token; neither your password nor a long-lived session
            is stored in browser storage.
          </p>
        </article>
      </div>
    </details>
  );
}

const inputClass =
  "h-11 w-full rounded-xl border border-border bg-white px-3.5 text-sm text-foreground outline-none transition focus:border-primary focus:ring-4 focus:ring-ring/30 dark:border-white/15 dark:bg-white/10 dark:focus:border-primary dark:focus:ring-ring/30";

export default function RepoAuthPage({ mode }: { mode: AuthMode }) {
  const queryClient = useQueryClient();
  const { theme, toggleTheme } = useTheme();
  const [, setLocation] = useLocation();
  const login = useMutation({ mutationFn: fastApi.auth.login });
  const register = useMutation({ mutationFn: fastApi.auth.register });
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [country, setCountry] = useState("");
  const [accountType, setAccountType] = useState<"individual" | "organization">(
    "individual"
  );
  const [organizationName, setOrganizationName] = useState("");
  const [selectedOrganizationId, setSelectedOrganizationId] = useState("");
  const [notice, setNotice] = useState("");
  const availableOrganizations = useQuery<OrganizationOption[]>({
    queryKey: ["fastapi", "organization", "list"],
    queryFn: async () =>
      (await fastApi.organization.list()) as OrganizationOption[],
    enabled: mode === "register",
  });

  const finishLogin = async () => {
    await queryClient.invalidateQueries({
      queryKey: ["fastapi", "auth", "me"],
    });
    setLocation("/");
  };

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setNotice("");
    try {
      await login.mutateAsync({ email, password });
      await finishLogin();
    } catch (error: any) {
      setNotice(
        error.message || "Unable to sign in. Check your email and password."
      );
    }
  };

  const handleRegister = async (event: FormEvent) => {
    event.preventDefault();
    setNotice("");
    if (!/[a-z]/.test(password) || !/[A-Z]/.test(password) || !/[0-9]/.test(password)) {
      setNotice("Your password needs 12+ characters with at least one uppercase letter, one lowercase letter, and one number.");
      return;
    }
    try {
      const payload: Record<string, string | undefined> = {
        name,
        email,
        password,
        country: country || undefined,
      };
      if (accountType === "individual" && selectedOrganizationId)
        payload.organizationId = selectedOrganizationId;
      await register.mutateAsync(payload);
      if (accountType === "organization")
        setNotice(
          "Your personal account was created. Organization roles remain approval-only to protect member data."
        );
      if (accountType === "individual" && selectedOrganizationId)
        setNotice("Account created. Your request to join the selected organization is now pending the administrator's approval.");
      await finishLogin();
    } catch (error: any) {
      setNotice(error.message || "Unable to create the account.");
    }
  };

  const submit = mode === "login" ? handleLogin : handleRegister;
  const isPending = login.isPending || register.isPending;
  const title =
    mode === "login"
      ? "Welcome back."
      : mode === "register"
        ? "Get started."
        : "Recover your account.";
  const subtitle =
    mode === "login"
      ? "Sign in to continue tracking your carbon footprint."
      : mode === "register"
        ? "Create your secure MongoDB-backed CarbonSense account."
        : "Password recovery will be available from the native account service.";

  return (
    <div className="cs-app-shell min-h-screen px-4 py-6 text-foreground dark:text-muted-foreground sm:px-6">
      <header className="mx-auto flex max-w-6xl items-center justify-between">
        <AuthBrand />
        <button
          onClick={() => toggleTheme?.()}
          className="grid h-10 w-10 place-items-center rounded-xl text-muted-foreground hover:bg-white/70 dark:hover:bg-white/10"
          aria-label="Toggle dark mode"
        >
          {theme === "dark" ? (
            <Sun size={18} className="text-amber-400" />
          ) : (
            <Moon size={18} />
          )}
        </button>
      </header>
      <main className="mx-auto flex min-h-[calc(100vh-7rem)] max-w-md items-center py-12">
        <section className="w-full">
          <Link
            href="/"
            className="mb-8 inline-flex items-center gap-1.5 text-sm font-semibold text-primary hover:underline"
          >
            <ArrowLeft size={15} /> Dashboard
          </Link>
          <div className="text-center">
            <span className="mx-auto grid h-16 w-16 place-items-center rounded-3xl bg-gradient-to-br from-emerald-500 to-emerald-800 text-white shadow-xl shadow-primary/20">
              {mode === "forgot" ? (
                <KeyRound size={30} />
              ) : mode === "register" ? (
                <Leaf size={31} />
              ) : (
                <LockKeyhole size={29} />
              )}
            </span>
            <h1 className="mt-5 text-4xl font-extrabold tracking-tight sm:text-5xl text-foreground">
              {title}
            </h1>
            <p className="mt-3 text-base leading-relaxed text-muted-foreground">
              {subtitle}
            </p>
          </div>

          {mode === "forgot" ? (
            <div className="cs-card mt-8 p-8">
              <p className="text-sm font-semibold text-foreground">
                Account recovery
              </p>
              <p className="mt-3 text-base leading-relaxed text-muted-foreground">
                The clean MongoDB-native account service is active.
                Password-recovery delivery will be added as a separate, verified
                email feature; credentials are never recoverable from the
                database.
              </p>
              <Link
                href="/login"
                className="mt-5 block text-center text-sm font-semibold text-primary hover:underline"
              >
                Return to sign in
              </Link>
            </div>
          ) : (
            <>
              <form
                onSubmit={submit}
                className="cs-card mt-8 space-y-5 p-7 sm:p-8"
              >
                {mode === "register" && (
                  <>
                    <div className="grid grid-cols-2 gap-2 rounded-2xl bg-muted p-1.5 dark:bg-white/5">
                      <button
                        type="button"
                        onClick={() => setAccountType("individual")}
                        className={`rounded-xl px-3 py-2.5 text-sm font-bold transition ${accountType === "individual" ? "bg-primary text-primary-foreground shadow" : "text-muted-foreground"}`}
                      >
                        <UserRound size={15} className="mr-1.5 inline" />
                        Individual
                      </button>
                      <button
                        type="button"
                        onClick={() => setAccountType("organization")}
                        className={`rounded-xl px-3 py-2.5 text-sm font-bold transition ${accountType === "organization" ? "bg-primary text-primary-foreground shadow" : "text-muted-foreground"}`}
                      >
                        <Building2 size={15} className="mr-1.5 inline" />
                        Organization
                      </button>
                    </div>
                    <Field label="Full name">
                      <input
                        className={inputClass}
                        required
                        minLength={2}
                        value={name}
                        onChange={event => setName(event.target.value)}
                        placeholder="Jane Doe"
                        autoComplete="name"
                      />
                    </Field>
                  </>
                )}
                <Field label="Email">
                  <span className="relative block">
                    <Mail
                      size={16}
                      className="absolute left-3.5 top-3 text-muted-foreground"
                    />
                    <input
                      className={`${inputClass} pl-10`}
                      required
                      type="email"
                      value={email}
                      onChange={event => setEmail(event.target.value)}
                      placeholder="you@example.com"
                      autoComplete="email"
                    />
                  </span>
                </Field>
                <Field
                  label="Password"
                  right={
                    mode === "login" ? (
                      <Link
                        href="/forgot-password"
                        className="text-xs font-bold text-primary hover:underline"
                      >
                        Forgot password?
                      </Link>
                    ) : undefined
                  }
                >
                  <input
                    className={inputClass}
                    required
                    type="password"
                    minLength={12}
                    maxLength={128}
                    value={password}
                    onChange={event => setPassword(event.target.value)}
                    placeholder={
                      mode === "register"
                        ? "12+ characters, upper/lowercase and number"
                        : "••••••••"
                    }
                    autoComplete={
                      mode === "login" ? "current-password" : "new-password"
                    }
                  />
                </Field>
                {mode === "register" && (
                  <>
                    <Field label="Country (optional)">
                      <select
                        className={inputClass}
                        value={country}
                        onChange={event => setCountry(event.target.value)}
                      >
                        <option value="">Select country</option>
                        {countries.map(item => (
                          <option key={item} value={item}>
                            {item}
                          </option>
                        ))}
                      </select>
                    </Field>
                    {accountType === "individual" && (
                      <Field label="Join an organization (optional)">
                        <select
                          className={inputClass}
                          value={selectedOrganizationId}
                          onChange={event =>
                            setSelectedOrganizationId(event.target.value)
                          }
                        >
                          <option value="">Join later</option>
                          {availableOrganizations.data?.map(org => (
                            <option key={org.id} value={org.id}>
                              {org.name} ({org.memberCount} members)
                            </option>
                          ))}
                        </select>
                      </Field>
                    )}
                    {accountType === "organization" && (
                      <Field label="Organization name">
                        <input
                          className={inputClass}
                          required
                          value={organizationName}
                          onChange={event =>
                            setOrganizationName(event.target.value)
                          }
                          placeholder="Green Earth NGO"
                          autoComplete="organization"
                        />
                      </Field>
                    )}
                    <p className="rounded-xl bg-primary/8 px-3.5 py-3 text-xs leading-5 text-primary dark:bg-primary/20">
                      Choose an available organization to join during sign-up,
                      or skip this step and join later from your organization
                      page.
                    </p>
                  </>
                )}
                {notice && (
                  <p className="rounded-xl bg-amber-50 px-3.5 py-3 text-sm text-amber-900 dark:bg-amber-950 dark:text-amber-100">
                    {notice}
                  </p>
                )}
                <button
                  disabled={isPending}
                  type="submit"
                  className="cs-action flex w-full items-center justify-center rounded-xl bg-primary px-4 py-3.5 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/20 transition-colors hover:bg-primary/90 disabled:cursor-wait disabled:opacity-70"
                >
                  {isPending
                    ? "Please wait…"
                    : mode === "login"
                      ? "Sign in"
                      : "Create account"}
                  <ArrowRight size={16} className="ml-2" />
                </button>
              </form>
              {mode === "login" && (
                <Link
                  href="/register"
                  className="cs-action-secondary mt-4 flex w-full items-center justify-center rounded-xl border border-primary bg-primary/8 px-4 py-3.5 text-sm font-bold text-primary hover:border-primary hover:bg-primary/10 dark:border-primary/25 dark:bg-primary/20"
                >
                  <UserRound size={17} className="mr-2" />
                  Create a CarbonSense account{" "}
                  <ArrowRight size={16} className="ml-2" />
                </Link>
              )}
              <p className="mt-6 text-center text-sm text-muted-foreground">
                {mode === "login" ? (
                  <>Use your secure CarbonSense email and password above.</>
                ) : (
                  <>
                    Already have an account?{" "}
                    <Link
                      href="/login"
                      className="font-bold text-primary hover:underline"
                    >
                      Sign in
                    </Link>
                  </>
                )}
              </p>
              <StorageBoundary />
            </>
          )}
        </section>
      </main>
    </div>
  );
}
