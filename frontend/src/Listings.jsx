import { useEffect, useState } from "react";
import {
  Search,
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  Building2,
} from "lucide-react";
import { get, number } from "./api";

export default function Listings({ cities, categories, revision }) {
  const [query, setQuery] = useState("");
  const [city, setCity] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setBusy(true);
    setError("");
    const timer = setTimeout(() => {
      const params = new URLSearchParams({
        q: query,
        city,
        category,
        page,
        page_size: 8,
      });
      get(`/listings?${params}`, controller.signal)
        .then(setData)
        .catch((err) => {
          if (err.name !== "AbortError") setError(err.message);
        })
        .finally(() => {
          if (!controller.signal.aborted) setBusy(false);
        });
    }, 200);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, city, category, page, revision, retry]);
  const change = (setter) => (event) => {
    setter(event.target.value);
    setPage(1);
  };
  const pages = Math.max(1, Math.ceil((data?.total || 0) / 8));
  return (
    <section
      className="panel directory"
      id="directory"
      aria-label="Business directory"
    >
      <div className="directory-heading">
        <div>
          <h2>Business directory</h2>
          <p>Explore the individual records behind the numbers.</p>
        </div>
        <span className="badge">
          {data ? `${number(data.total)} records` : "Loading records"}
        </span>
      </div>
      <div className="filters">
        <label className="search">
          <Search size={17} />
          <input
            aria-label="Search businesses"
            value={query}
            onChange={change(setQuery)}
            placeholder="Search business name…"
          />
        </label>
        <select
          aria-label="Filter by city"
          value={city}
          onChange={change(setCity)}
        >
          <option value="">All cities</option>
          {cities.map((item) => (
            <option key={item.name}>{item.name}</option>
          ))}
        </select>
        <select
          aria-label="Filter by category"
          value={category}
          onChange={change(setCategory)}
        >
          <option value="">All categories</option>
          {categories.map((item) => (
            <option key={item.name}>{item.name}</option>
          ))}
        </select>
        {(query || city || category) && (
          <button
            className="text-button"
            onClick={() => {
              setQuery("");
              setCity("");
              setCategory("");
              setPage(1);
            }}
          >
            Clear filters
          </button>
        )}
      </div>
      {error ? (
        <div className="table-message" role="alert">
          {error}
          <button
            className="button"
            onClick={() => setRetry((value) => value + 1)}
          >
            Try again
          </button>
        </div>
      ) : (
        <div className="table-scroll" aria-busy={busy}>
          <table>
            <thead>
              <tr>
                <th>Business name</th>
                <th>Category</th>
                <th>City</th>
                <th>Address</th>
                <th>Phone</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {busy
                ? Array.from({ length: 5 }, (_, index) => (
                    <tr key={index} className="skeleton-row">
                      <td colSpan="6">
                        <span />
                      </td>
                    </tr>
                  ))
                : data?.items.map((item) => (
                    <tr key={item.id}>
                      <td className="business-cell">
                        <span className="business-icon">
                          <Building2 size={16} />
                        </span>
                        <strong>{item.business_name}</strong>
                      </td>
                      <td>
                        <span className="category-tag">{item.category}</span>
                      </td>
                      <td>{item.city}</td>
                      <td className="address-cell">{item.address}</td>
                      <td className="phone-cell">
                        {item.phone || (
                          <span className="muted">Not supplied</span>
                        )}
                      </td>
                      <td>
                        {item.source_url ? (
                          <a
                            className="source-link"
                            href={item.source_url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {item.source}
                            <ArrowUpRight size={13} />
                          </a>
                        ) : (
                          item.source
                        )}
                      </td>
                    </tr>
                  ))}
            </tbody>
          </table>
          {!busy && !data?.items.length && (
            <div className="table-message">
              No businesses match these filters. Try a different name or clear
              your filters.
            </div>
          )}
        </div>
      )}
      <div className="table-footer">
        <span aria-live="polite">
          {busy
            ? "Loading listings…"
            : `${number(data?.total ? (page - 1) * 8 + 1 : 0)}–${number(Math.min(page * 8, data?.total || 0))} of ${number(data?.total || 0)} records`}
        </span>
        <div>
          <button
            className="page-button"
            aria-label="Previous page"
            disabled={page <= 1 || busy}
            onClick={() => setPage((value) => value - 1)}
          >
            <ChevronLeft size={16} />
          </button>
          <span>
            Page {page} of {pages}
          </span>
          <button
            className="page-button"
            aria-label="Next page"
            disabled={page >= pages || busy}
            onClick={() => setPage((value) => value + 1)}
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </section>
  );
}
