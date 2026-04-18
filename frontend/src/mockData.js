export const endpointCards = [
  {
    method: "GET",
    route: "/health",
    summary: "Operational readiness signal for runtime checks and monitoring.",
  },
  {
    method: "GET",
    route: "/config-summary",
    summary: "Safe environment profile for verification and support workflows.",
  },
  {
    method: "POST",
    route: "/fetch",
    summary: "Authenticated request execution with refresh and retry handling.",
  },
  {
    method: "POST",
    route: "/fetch-paginated",
    summary: "Sequential page retrieval for processing and export preparation.",
  },
  {
    method: "POST",
    route: "/export/json",
    summary: "Structured payload delivery for downstream integrations and storage.",
  },
  {
    method: "POST",
    route: "/export/csv",
    summary: "Tabular export for reporting and spreadsheet-oriented operations.",
  },
];

export const runtimeEvents = [
  {
    time: "09:18",
    title: "OAuth credentials initialized",
    detail: "Scope-aware auth profile prepared for token exchange.",
    level: "good",
  },
  {
    time: "09:24",
    title: "Retry policy active",
    detail: "Transient upstream failures are handled with exponential backoff.",
    level: "neutral",
  },
  {
    time: "09:31",
    title: "CSV export prepared",
    detail: "Paginated payloads normalized into a downstream-ready report file.",
    level: "accent",
  },
];
