import { useEffect, useMemo, useState } from "react";
import { endpointCards, runtimeEvents } from "./mockData";

const baseUrl = "http://127.0.0.1:8000";

const demoConfig = {
  auth_mode: "oauth_client_credentials",
  proxy_enabled: true,
  request_timeout: 30,
  max_retries: 2,
  api_data_path: "/v1/data",
  api_base_url: "https://api.acme-integrations.com",
};

const demoResponse = {
  success: true,
  path: "/v1/data",
  data: {
    items: [
      { id: "cus_1024", status: "active", plan: "enterprise" },
      { id: "cus_1025", status: "trial", plan: "growth" },
    ],
    page: 1,
    total: 248,
  },
};

function formatAuthMode(value) {
  if (!value) return "Basic Token";
  if (value === "oauth_client_credentials") return "OAuth Client Credentials";
  if (value === "basic") return "Basic Token";
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function StatusBadge({ online, demoMode }) {
  const label = online ? "Connected" : demoMode ? "Demo Mode" : "Offline";
  return (
    <span className={`status-badge ${online ? "online" : demoMode ? "demo" : "offline"}`}>
      <span className="status-dot" />
      {label}
    </span>
  );
}

function SectionTitle({ title, subtitle, action }) {
  return (
    <div className="section-title">
      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
      {action ? <div>{action}</div> : null}
    </div>
  );
}

function App() {
  const [health, setHealth] = useState({ status: "Checking", service: "secure-backend" });
  const [configSummary, setConfigSummary] = useState(null);
  const [fetchResult, setFetchResult] = useState({
    message: "Run a fetch preview to inspect the live backend response.",
  });
  const [requestDraft, setRequestDraft] = useState({
    path: "/v1/data",
    params: '{\n  "limit": 5,\n  "page": 1\n}',
  });
  const [activeView, setActiveView] = useState("overview");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  const [responseView, setResponseView] = useState("json");
  const [previewMode, setPreviewMode] = useState("presentation");

  useEffect(() => {
    let cancelled = false;

    async function hydrate() {
      try {
        const [healthResponse, configResponse] = await Promise.all([
          fetch(`${baseUrl}/health`),
          fetch(`${baseUrl}/config-summary`),
        ]);
        const [healthJson, configJson] = await Promise.all([
          healthResponse.json(),
          configResponse.json(),
        ]);

        if (cancelled) return;
        setHealth(healthJson);
        setConfigSummary(configJson);
        setDemoMode(false);
      } catch {
        if (cancelled) return;
        setHealth({ status: "Demo", service: "integration-console-demo" });
        setConfigSummary(demoConfig);
        setFetchResult(demoResponse);
        setDemoMode(true);
      }
    }

    hydrate();
    return () => {
      cancelled = true;
    };
  }, []);

  async function runFetchPreview(event) {
    event.preventDefault();

    let parsedParams = null;
    try {
      parsedParams = requestDraft.params.trim() ? JSON.parse(requestDraft.params) : null;
    } catch {
      setFetchResult({ error: "Params must be valid JSON before sending the request." });
      return;
    }

    if (demoMode) {
      setFetchResult({
        ...demoResponse,
        data: {
          ...demoResponse.data,
          filters: parsedParams,
          path: requestDraft.path,
          note: "Demo mode is active. Start FastAPI to switch this panel to live backend data.",
        },
      });
      return;
    }

    setIsSubmitting(true);
    setFetchResult({ message: "Submitting request..." });

    try {
      const response = await fetch(`${baseUrl}/fetch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: requestDraft.path,
          params: parsedParams,
        }),
      });

      const data = await response.json();
      setFetchResult(data);
    } catch {
      setFetchResult({
        error: "The FastAPI backend is not reachable. Start it to enable live preview.",
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  const topMetrics = useMemo(
    () => [
      {
        label: "Auth Strategy",
        value: formatAuthMode(configSummary?.auth_mode),
        detail: "Basic + OAuth client credentials",
      },
      {
        label: "Retry Policy",
        value: `${configSummary?.max_retries ?? 2} attempts`,
        detail: "Exponential backoff supported",
      },
      {
        label: "Exports",
        value: "JSON / CSV",
        detail: "Paginated retrieval pipeline",
      },
      {
        label: "Verification",
        value: "21 tests",
        detail: "Backend behaviors covered",
      },
    ],
    [configSummary],
  );

  const navItems = [
    { id: "overview", label: "Overview" },
    { id: "request-builder", label: "Request Builder" },
    { id: "endpoints", label: "Endpoints" },
    { id: "exports", label: "Exports" },
  ];

  const workspaceTitle = {
    overview: "Enterprise integration tooling for auth, retrieval, and export.",
    "request-builder": "Compose and inspect authenticated requests through a controlled workflow.",
    endpoints: "Review the backend surface through a product-style API catalog.",
    exports: "Present downstream delivery formats in a cleaner operations workspace.",
  }[activeView];

  const responseRows = Array.isArray(fetchResult?.data?.items)
    ? fetchResult.data.items
    : Array.isArray(fetchResult?.data)
      ? fetchResult.data
      : [];

  const visibleResponse =
    previewMode === "blank"
      ? { message: demoMode ? "Switch back to Presentation Preview to show the demo payload." : "Live response view is waiting for the next request." }
      : fetchResult;

  return (
    <div className="console-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">SI</div>
          <div>
            <p className="brand-kicker">Secure API Integration</p>
            <h1>Control Console</h1>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={activeView === item.id ? "nav-item active" : "nav-item"}
              onClick={() => setActiveView(item.id)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-card">
          <p className="card-label">Runtime</p>
          <StatusBadge demoMode={demoMode} online={!demoMode && health.status === "ok"} />
          <dl>
            <div>
              <dt>Service</dt>
              <dd>{health.service}</dd>
            </div>
            <div>
              <dt>Base URL</dt>
              <dd>{configSummary?.api_base_url ?? "Loading..."}</dd>
            </div>
          </dl>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div className="topbar-copy">
            <div className="header-kicker-row">
              <p className="page-label">Operational Workspace</p>
              <span className="header-chip">Integration Console</span>
            </div>
            <h2>{workspaceTitle}</h2>
          </div>
          <div className="topbar-actions">
            <StatusBadge demoMode={demoMode} online={!demoMode && health.status === "ok"} />
            <button className="ghost-button" type="button">
              {demoMode ? "Demo Dataset Active" : "Live Backend Mode"}
            </button>
          </div>
        </header>

        <section className="metric-row">
          {topMetrics.map((metric) => (
            <article className="metric-panel" key={metric.label}>
              <span className="metric-label">{metric.label}</span>
              <strong>{metric.value}</strong>
              <small>{metric.detail}</small>
            </article>
          ))}
        </section>

        {activeView === "overview" ? (
          <section className="workspace-grid">
            <div className="column-stack">
              <section className="panel">
                <SectionTitle
                  title="Connection Profile"
                  subtitle="Backend configuration surfaced in a way a real product team could use."
                />
                <div className="detail-grid">
                  <article>
                    <span>Auth Mode</span>
                    <strong className="compact-value">
                      {formatAuthMode(configSummary?.auth_mode)}
                    </strong>
                  </article>
                  <article>
                    <span>Proxy</span>
                    <strong>{configSummary?.proxy_enabled ? "Enabled" : "Disabled"}</strong>
                  </article>
                  <article>
                    <span>Timeout</span>
                    <strong>{configSummary?.request_timeout ?? "--"}s</strong>
                  </article>
                  <article>
                    <span>Retry Count</span>
                    <strong>{configSummary?.max_retries ?? "--"}</strong>
                  </article>
                </div>
              </section>

              <section className="panel">
                <SectionTitle
                  title="Endpoint Catalog"
                  subtitle="Focused documentation framing instead of decorative cards."
                />
                <div className="endpoint-table">
                  <div className="endpoint-table-head">
                    <span>Method</span>
                    <span>Route</span>
                    <span>Purpose</span>
                  </div>
                  {endpointCards.map((endpoint) => (
                    <div className="endpoint-row" key={endpoint.route}>
                      <span className={`method-badge ${endpoint.method.toLowerCase()}`}>
                        {endpoint.method}
                      </span>
                      <code>{endpoint.route}</code>
                      <p>{endpoint.summary}</p>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            <div className="column-stack">
            <section className="panel result-panel">
              <SectionTitle
                title="Response Inspector"
                subtitle="A clean operator-facing output view for debugging and demos."
                action={demoMode ? <span className="mini-badge">Demo data</span> : null}
              />
              <div className="response-toolbar">
                <button
                  className={responseView === "json" ? "response-chip interactive active" : "response-chip interactive"}
                  onClick={() => setResponseView("json")}
                  type="button"
                >
                  Structured JSON
                </button>
                <button
                  className={responseView === "table" ? "response-chip interactive active" : "response-chip interactive"}
                  onClick={() => setResponseView("table")}
                  type="button"
                >
                  Table View
                </button>
                <button
                  className={previewMode === "presentation" ? "response-chip subtle interactive active" : "response-chip subtle interactive"}
                  onClick={() => setPreviewMode("presentation")}
                  type="button"
                >
                  Presentation-ready Preview
                </button>
                <button
                  className={previewMode === "blank" ? "response-chip subtle interactive active" : "response-chip subtle interactive"}
                  onClick={() => setPreviewMode("blank")}
                  type="button"
                >
                  Blank / Live State
                </button>
              </div>
              {responseView === "json" || responseRows.length === 0 ? (
                <pre className="response-viewer">{JSON.stringify(visibleResponse, null, 2)}</pre>
              ) : (
                <div className="table-viewer">
                  <div className="table-viewer-head">
                    {Object.keys(responseRows[0]).map((key) => (
                      <span key={key}>{key}</span>
                    ))}
                  </div>
                  {responseRows.map((row) => (
                    <div className="table-viewer-row" key={row.id ?? JSON.stringify(row)}>
                      {Object.entries(row).map(([key, value]) => (
                        <span key={key}>{String(value)}</span>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </section>

              <section className="panel">
                <SectionTitle
                  title="Runtime Activity"
                  subtitle="Short log feed to make the app feel like a credible integration tool."
                />
                <div className="runtime-list">
                  {runtimeEvents.map((event) => (
                    <article className="runtime-row" key={event.title}>
                      <div className={`runtime-mark ${event.level}`} />
                      <div>
                        <strong>{event.title}</strong>
                        <p>{event.detail}</p>
                      </div>
                      <time>{event.time}</time>
                    </article>
                  ))}
                </div>
              </section>
            </div>
          </section>
        ) : null}

        {activeView === "request-builder" ? (
          <section className="single-view-grid">
            <section className="panel">
              <SectionTitle
                title="Request Builder"
                subtitle="Use the same UI to demonstrate token flows, fetch behavior, and backend response formatting."
                action={<span className="mini-badge">{demoMode ? "Demo preview" : "Live preview"}</span>}
              />

              <form className="builder-form" onSubmit={runFetchPreview}>
                <label>
                  Request path
                  <input
                    value={requestDraft.path}
                    onChange={(event) =>
                      setRequestDraft((current) => ({ ...current, path: event.target.value }))
                    }
                    placeholder="/v1/data"
                  />
                </label>

                <label>
                  Query params JSON
                  <textarea
                    rows={10}
                    value={requestDraft.params}
                    onChange={(event) =>
                      setRequestDraft((current) => ({ ...current, params: event.target.value }))
                    }
                  />
                </label>

                <div className="form-actions">
                  <button className="primary-button clean" disabled={isSubmitting} type="submit">
                    {isSubmitting ? "Running..." : "Run Request"}
                  </button>
                  <button
                    className="ghost-button"
                    onClick={() =>
                      setRequestDraft({
                        path: "/v1/data",
                        params: '{\n  "limit": 5,\n  "page": 1\n}',
                      })
                    }
                    type="button"
                  >
                    Reset
                  </button>
                </div>
              </form>
            </section>

            <section className="panel result-panel">
              <SectionTitle
                title="Request Result"
                subtitle="Inspect the payload generated by the current request draft."
              />
              <div className="response-toolbar">
                <button
                  className={responseView === "json" ? "response-chip interactive active" : "response-chip interactive"}
                  onClick={() => setResponseView("json")}
                  type="button"
                >
                  Structured JSON
                </button>
                <button
                  className={responseView === "table" ? "response-chip interactive active" : "response-chip interactive"}
                  onClick={() => setResponseView("table")}
                  type="button"
                >
                  Table View
                </button>
                <button
                  className={previewMode === "presentation" ? "response-chip subtle interactive active" : "response-chip subtle interactive"}
                  onClick={() => setPreviewMode("presentation")}
                  type="button"
                >
                  {demoMode ? "Demo-backed Response" : "Live Backend Output"}
                </button>
                <button
                  className={previewMode === "blank" ? "response-chip subtle interactive active" : "response-chip subtle interactive"}
                  onClick={() => setPreviewMode("blank")}
                  type="button"
                >
                  Blank / Live State
                </button>
              </div>
              {responseView === "json" || responseRows.length === 0 ? (
                <pre className="response-viewer">{JSON.stringify(visibleResponse, null, 2)}</pre>
              ) : (
                <div className="table-viewer">
                  <div className="table-viewer-head">
                    {Object.keys(responseRows[0]).map((key) => (
                      <span key={key}>{key}</span>
                    ))}
                  </div>
                  {responseRows.map((row) => (
                    <div className="table-viewer-row" key={row.id ?? JSON.stringify(row)}>
                      {Object.entries(row).map(([key, value]) => (
                        <span key={key}>{String(value)}</span>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </section>
          </section>
        ) : null}

        {activeView === "endpoints" ? (
          <section className="panel">
            <SectionTitle
              title="API Surface Map"
              subtitle="A complete route catalog for technical review and client walkthroughs."
            />
            <div className="endpoint-table">
              <div className="endpoint-table-head">
                <span>Method</span>
                <span>Route</span>
                <span>Purpose</span>
              </div>
              {endpointCards.map((endpoint) => (
                <div className="endpoint-row" key={endpoint.route}>
                  <span className={`method-badge ${endpoint.method.toLowerCase()}`}>
                    {endpoint.method}
                  </span>
                  <code>{endpoint.route}</code>
                  <p>{endpoint.summary}</p>
                </div>
              ))}
            </div>
          </section>
        ) : null}

        {activeView === "exports" ? (
          <section className="single-view-grid">
            <section className="panel">
              <SectionTitle
                title="Export Workspace"
                subtitle="How the integration turns retrieved data into deliverables for downstream teams."
              />
              <div className="export-list">
                <article className="export-card">
                  <div>
                    <span className="card-label">JSON Export</span>
                    <strong>Structured archival and app-to-app delivery</strong>
                  </div>
                  <p>Preserves nested payloads for audits, storage, and downstream ingestion.</p>
                </article>
                <article className="export-card">
                  <div>
                    <span className="card-label">CSV Export</span>
                    <strong>Operational reporting and spreadsheet workflows</strong>
                  </div>
                  <p>Flattens paginated output into a business-friendly handoff format.</p>
                </article>
              </div>
            </section>

            <section className="panel">
              <SectionTitle
                title="Export Readiness"
                subtitle="A concise view of what makes the export pipeline production-friendly."
              />
              <div className="detail-grid detail-grid-two">
                <article>
                  <span>Pagination</span>
                  <strong>Supported</strong>
                </article>
                <article>
                  <span>Formats</span>
                  <strong>JSON / CSV</strong>
                </article>
                <article>
                  <span>Retries</span>
                  <strong>Included</strong>
                </article>
                <article>
                  <span>Auditability</span>
                  <strong>Structured logs</strong>
                </article>
              </div>
            </section>
          </section>
        ) : null}
      </div>
    </div>
  );
}

export default App;
