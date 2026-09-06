export class FastApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
    this.name = "FastApiError";
  }
}

export type FastApiUser = {
  id: string;
  email: string;
  name: string;
  role: "individual" | "org_admin" | "super_admin";
  organizationId: string | null;
  country: string | null;
  region: "mixed" | "renewable_heavy" | null;
  shareAggregates: boolean;
  isActive: boolean;
  createdAt: string;
};

export type FastApiAuthResponse = { user: FastApiUser; csrf_token: string };

type RequestOptions = Omit<RequestInit, "body" | "headers"> & {
  body?: unknown;
  headers?: HeadersInit;
};

function csrfToken() {
  const cookie = document.cookie
    .split(";")
    .map(value => value.trim())
    .find(value => value.startsWith("cs_csrf="));
  return cookie
    ? decodeURIComponent(cookie.slice("cs_csrf=".length))
    : undefined;
}

export async function fastApiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const method = options.method ?? "GET";
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.body !== undefined)
    headers.set("Content-Type", "application/json");
  if (!["GET", "HEAD", "OPTIONS"].includes(method.toUpperCase())) {
    const token = csrfToken();
    if (token) headers.set("X-CSRF-Token", token);
  }
  const response = await fetch(`/api/v1${path}`, {
    ...options,
    method,
    headers,
    credentials: "include",
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  if (response.status === 204) return undefined as T;
  const raw = await response.text();
  let payload: { detail?: string } | T = {};
  try {
    payload = raw ? JSON.parse(raw) : {};
  } catch {
    if (!response.ok) {
      throw new FastApiError(
        response.status,
        `The service returned a non-JSON response (${response.status}). Check the FastAPI service logs.`
      );
    }
    throw new FastApiError(
      response.status,
      "The service returned an invalid JSON response. Check the FastAPI service logs."
    );
  }
  const detail =
    typeof payload === "object" && payload !== null && "detail" in payload
      ? String(
          (payload as { detail?: unknown }).detail ||
            "The request could not be completed."
        )
      : "The request could not be completed.";
  if (!response.ok) throw new FastApiError(response.status, detail);
  return payload as T;
}

export const fastApi = {
  auth: {
    register: (input: unknown) =>
      fastApiRequest<FastApiAuthResponse>("/auth/register", {
        method: "POST",
        body: input,
      }),
    login: (input: unknown) =>
      fastApiRequest<FastApiAuthResponse>("/auth/login", {
        method: "POST",
        body: input,
      }),
    me: () => fastApiRequest<FastApiUser>("/auth/me"),
    refresh: () =>
      fastApiRequest<FastApiAuthResponse>("/auth/refresh", { method: "POST" }),
    logout: () => fastApiRequest<void>("/auth/logout", { method: "POST" }),
  },
  model: {
    info: () => fastApiRequest("/model/info"),
    predict: (input: unknown) =>
      fastApiRequest("/model/predict", { method: "POST", body: input }),
    explain: (input: unknown) =>
      fastApiRequest("/model/explain", { method: "POST", body: input }),
    baseline: (input: unknown) =>
      fastApiRequest("/model/baseline", { method: "POST", body: input }),
  },
  planning: {
    latestCompleted: () => fastApiRequest("/planning/latest-completed"),
    optimize: (input: unknown) =>
      fastApiRequest("/planning/optimize", { method: "POST", body: input }),
    whatIf: (input: unknown) =>
      fastApiRequest("/planning/what-if", { method: "POST", body: input }),
    actionPlan: (input: unknown) =>
      fastApiRequest("/planning/action-plan", { method: "POST", body: input }),
    netZero: (input: unknown) =>
      fastApiRequest("/planning/net-zero", { method: "POST", body: input }),
  },
  activity: {
    list: () => fastApiRequest("/activity"),
    create: (input: unknown) =>
      fastApiRequest("/activity", { method: "POST", body: input }),
    remove: (id: string) =>
      fastApiRequest(`/activity/${id}`, { method: "DELETE" }),
    summary: () => fastApiRequest("/activity/summary"),
    progress: () => fastApiRequest("/activity/progress"),
    questSummary: () => fastApiRequest("/activity/quest-summary"),
  },
  goals: {
    list: () => fastApiRequest("/goals"),
    create: (input: unknown) =>
      fastApiRequest("/goals", { method: "POST", body: input }),
  },
  insights: {
    history: () => fastApiRequest("/insights/history"),
    forecast: () => fastApiRequest("/insights/forecast"),
  },
  history: {
    list: () => fastApiRequest("/history"),
    clear: () => fastApiRequest("/history", { method: "DELETE" }),
  },
  privacy: {
    get: () => fastApiRequest("/privacy"),
    update: (input: unknown) =>
      fastApiRequest("/privacy", { method: "PATCH", body: input }),
  },
  assistant: {
    chat: (input: unknown) =>
      fastApiRequest("/assistant/chat", { method: "POST", body: input }),
  },
  recommendations: {
    catalog: () => fastApiRequest("/recommendations/catalog"),
    resultLed: () => fastApiRequest("/recommendations/result-led"),
    mine: () => fastApiRequest("/recommendations/mine"),
    organizationOverview: () =>
      fastApiRequest("/recommendations/organization-overview"),
    accept: (input: unknown) =>
      fastApiRequest("/recommendations/accept", {
        method: "POST",
        body: input,
      }),
    complete: (id: string, input: unknown) =>
      fastApiRequest(`/recommendations/${id}/complete`, {
        method: "POST",
        body: input,
      }),
    verify: (id: string) =>
      fastApiRequest(`/recommendations/${id}/verify`, { method: "POST" }),
    assign: (input: unknown) =>
      fastApiRequest("/recommendations/assign", {
        method: "POST",
        body: input,
      }),
  },
  reports: {
    mine: () => fastApiRequest("/reports/mine"),
    admin: () => fastApiRequest("/reports/admin"),
    create: (input: unknown) =>
      fastApiRequest("/reports", { method: "POST", body: input }),
    update: (id: string, input: unknown) =>
      fastApiRequest(`/reports/${id}`, { method: "PATCH", body: input }),
  },
  profile: {
    update: (input: unknown) =>
      fastApiRequest("/profile", { method: "PATCH", body: input }),
  },
  admin: {
    dashboard: () => fastApiRequest("/admin/dashboard"),
    users: () => fastApiRequest("/admin/users"),
    audit: () => fastApiRequest("/admin/audit"),
    updateRole: (id: string, input: unknown) =>
      fastApiRequest(`/admin/users/${id}/role`, {
        method: "PATCH",
        body: input,
      }),
    updateActive: (id: string, input: unknown) =>
      fastApiRequest(`/admin/users/${id}/active`, {
        method: "PATCH",
        body: input,
      }),
  },
  organization: {
    summary: () => fastApiRequest("/organization/summary"),
    summaries: () => fastApiRequest("/organization/summaries"),
    contributors: (params = "") =>
      fastApiRequest(`/organization/contributors${params}`),
    quests: (params = "") => fastApiRequest(`/organization/quests${params}`),
    me: () => fastApiRequest("/organization/me"),
    list: () => fastApiRequest("/organization/list"),
    members: () => fastApiRequest("/organization/members"),
    create: (input: unknown) =>
      fastApiRequest("/organization/create", { method: "POST", body: input }),
    join: (input: unknown) =>
      fastApiRequest("/organization/join", { method: "POST", body: input }),
    myJoinRequest: () => fastApiRequest("/organization/join-requests/mine"),
    joinRequests: () => fastApiRequest("/organization/join-requests"),
    decideJoinRequest: (id: string, decision: "approved" | "rejected") =>
      fastApiRequest(`/organization/join-requests/${id}/decision`, {
        method: "POST",
        body: { decision },
      }),
    leave: () => fastApiRequest("/organization/leave", { method: "POST" }),
    availableIndividuals: () => fastApiRequest("/organization/available-individuals"),
    inviteIndividual: (input: unknown) =>
      fastApiRequest("/organization/invite", { method: "POST", body: input }),
    organizationInvitations: () => fastApiRequest("/organization/invitations"),
    myInvitations: () => fastApiRequest("/organization/invitations/mine"),
    decideInvitation: (id: string, decision: "accepted" | "declined") =>
      fastApiRequest(`/organization/invitations/${id}/decision`, {
        method: "POST",
        body: { decision },
      }),
    reminders: () => fastApiRequest("/organization/reminders"),
    createReminder: (input: unknown) =>
      fastApiRequest("/organization/reminders", {
        method: "POST",
        body: input,
      }),
    acknowledgeReminder: (id: string) =>
      fastApiRequest(`/organization/reminders/${id}/acknowledge`, {
        method: "POST",
      }),
    dismissReminder: (id: string) =>
      fastApiRequest(`/organization/reminders/${id}/dismiss`, {
        method: "POST",
      }),
  },
};
