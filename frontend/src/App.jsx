import {
  lazy,
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Hexagon,
  LayoutDashboard,
  Shapes,
  List,
  ArrowUpRight,
  RefreshCw,
  Building2,
  MapPin,
  Layers,
  Phone,
  AlertCircle,
  Database,
} from "lucide-react";
import { get, number } from "./api";
import Listings from "./Listings";

const Charts = lazy(() => import("./Charts"));

function Stat({ icon: Icon, label, value, note, accent }) {
  return (
    <article className="stat">
      <div className="stat-top">
        <span>{label}</span>
        <span className={`stat-icon ${accent || ""}`}>
          <Icon size={18} />
        </span>
      </div>
      <strong>{number(value)}</strong>
      <p>{note}</p>
    </article>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updated, setUpdated] = useState(null);
  const [revision, setRevision] = useState(0);
  const pending = useRef(null);
  const refresh = useCallback(async () => {
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    setLoading(true);
    setError("");
    try {
      const result = await get("/dashboard", controller.signal);
      setData(result);
      setUpdated(new Date());
      setRevision((value) => value + 1);
    } catch (err) {
      if (err.name !== "AbortError") setError(err.message);
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }, []);
  useEffect(() => {
    refresh();
    return () => pending.current?.abort();
  }, [refresh]);
  const summary = data?.summary;
  return (
    <div className="app-shell">
      <a href="#overview" className="skip-link">
        Skip to dashboard
      </a>
      <aside className="sidebar">
        <a className="brand" href="#overview">
          <span className="brand-mark">
            <Hexagon size={25} strokeWidth={2.8} />
            <span />
          </span>
          <div>
            honeybee<span>DIGITAL · DATA WORKSPACE</span>
          </div>
        </a>
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          <a className="nav-item active" href="#overview">
            <LayoutDashboard size={18} />
            Overview
            <span className="nav-dot" />
          </a>
          <a className="nav-item" href="#categories">
            <Shapes size={18} />
            Categories
          </a>
          <a className="nav-item" href="#directory">
            <List size={18} />
            Business directory
          </a>
        </nav>
        <div className="sidebar-bottom">
          <div className="project-note">
            <span className="tiny-label">THE PROJECT</span>
            <h3>Business Listings</h3>
            <p>Directory data, organised into a clear view.</p>
            <span className="stack-label">React · FastAPI · MySQL</span>
          </div>
          <a
            href="https://www.openstreetmap.org/copyright"
            target="_blank"
            rel="noreferrer"
          >
            Open data attribution
            <ArrowUpRight size={14} />
          </a>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <span>
            Workspace <span className="crumb-slash">/</span>{" "}
            <strong>Business Listings</strong>
          </span>
          <span className="environment">
            <span />
            Local workspace
          </span>
        </header>
        <main id="overview">
          <div className="page-heading">
            <div>
              <div className="eyebrow">BUSINESS INTELLIGENCE</div>
              <h1>
                Listings overview<span>.</span>
              </h1>
              <p>
                A clear picture of your business directory, from the ground up.
              </p>
            </div>
            <button
              className="button refresh"
              disabled={loading}
              onClick={refresh}
            >
              <RefreshCw size={15} className={loading ? "rotating" : ""} />
              {loading ? "Refreshing…" : "Refresh data"}
            </button>
          </div>
          <div className="data-status">
            <span className={`status-dot ${error ? "failed" : ""}`} />
            <span>
              {error
                ? "Connection needs attention"
                : loading
                  ? "Fetching current database records"
                  : "Live database snapshot"}
            </span>
            {updated && (
              <span className="updated">
                Refreshed{" "}
                {updated.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            )}
          </div>
          {error && (
            <div className="error-banner" role="alert">
              <AlertCircle size={20} />
              <div>
                <strong>We couldn’t refresh your data.</strong>
                <p>
                  {error}
                  {data ? " The previous snapshot remains visible." : ""}
                </p>
              </div>
              <button className="button" onClick={refresh}>
                Try again
              </button>
            </div>
          )}
          {!data && loading ? (
            <div
              className="loading-layout"
              role="status"
              aria-label="Loading dashboard"
            >
              <div className="stats-grid">
                {[1, 2, 3, 4].map((n) => (
                  <div className="stat skeleton-card" key={n}>
                    <span />
                    <span />
                    <span />
                  </div>
                ))}
              </div>
              <div className="panel skeleton-chart" />
              <p>Loading business analytics…</p>
            </div>
          ) : (
            summary && (
              <>
                <div className="stats-grid">
                  <Stat
                    icon={Building2}
                    label="Total businesses"
                    value={summary.total}
                    note="Unique listings in the database"
                    accent="honey"
                  />
                  <Stat
                    icon={MapPin}
                    label="Cities covered"
                    value={summary.cities}
                    note="Tagged cities or collection areas"
                  />
                  <Stat
                    icon={Layers}
                    label="Business categories"
                    value={summary.categories}
                    note="Distinct categories represented"
                  />
                  <Stat
                    icon={Phone}
                    label="Phone available"
                    value={summary.with_phone}
                    note={`${summary.total ? ((summary.with_phone / summary.total) * 100).toFixed(1) : "0"}% of listings have a supplied phone`}
                  />
                </div>
                {summary.total > 0 ? (
                  <>
                    <div className="section-label">
                      <h2>Directory insights</h2>
                      <span>All listings · unfiltered totals</span>
                    </div>
                    <Suspense
                      fallback={
                        <div className="panel skeleton-chart" role="status">
                          Loading charts…
                        </div>
                      }
                    >
                      <Charts
                        cities={data.cities}
                        categories={data.categories}
                        sources={data.sources}
                      />
                    </Suspense>
                  </>
                ) : (
                  <section className="panel empty-state">
                    <Database size={30} />
                    <h2>Your directory is ready for data.</h2>
                    <p>
                      Import the collected dataset, then refresh to see your
                      analytics.
                    </p>
                  </section>
                )}
                <Listings
                  cities={data.cities.items}
                  categories={data.categories.items}
                  revision={revision}
                />
              </>
            )
          )}
          <footer>
            <span>
              Business Listings Dashboard <span className="footer-dot">·</span>{" "}
              Honeybee Digital assessment
            </span>
            <span>
              Data ©{" "}
              <a
                href="https://www.openstreetmap.org/copyright"
                target="_blank"
                rel="noreferrer"
              >
                OpenStreetMap contributors
              </a>{" "}
              ·{" "}
              <a
                href="https://opendatacommons.org/licenses/odbl/1-0/"
                target="_blank"
                rel="noreferrer"
              >
                ODbL 1.0
              </a>
            </span>
          </footer>
        </main>
      </div>
    </div>
  );
}
