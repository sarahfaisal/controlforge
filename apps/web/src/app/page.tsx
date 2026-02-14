"use client";

import { useEffect, useState } from "react";
import { fetchIndustries, fetchProjects } from "../lib/api";

export default function HomePage() {
  const [industries, setIndustries] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [i, p] = await Promise.all([fetchIndustries(), fetchProjects()]);
        setIndustries(i.industries || []);
        setProjects(p.projects || []);
      } catch (e: any) {
        setErr(e.message || String(e));
      }
    })();
  }, []);

  return (
    <main className="container">
      {err && (
        <div className="card" style={{ borderColor: "#fecaca", background: "#fff1f2" }}>
          <div style={{ fontWeight: 700 }}>API error</div>
          <div className="small">{err}</div>
          <div className="small" style={{ marginTop: 8 }}>
            Ensure the API is running on <code>http://localhost:8000</code> or set{" "}
            <code>NEXT_PUBLIC_API_BASE</code>.
          </div>
        </div>
      )}

      <div className="grid grid2" style={{ marginTop: 16 }}>
        <section className="card">
          <div className="hstack" style={{ justifyContent: "space-between" }}>
            <h2 style={{ margin: 0 }}>Projects</h2>
            <a className="btn btnPrimary" href="/new">New</a>
          </div>
          <div className="small">File-based workspaces under <code>workspaces/</code>.</div>
          <hr />
          {projects.length === 0 ? (
            <div className="small">No projects yet. Create one.</div>
          ) : (
            <div className="grid">
              {projects.map((p) => (
                <a key={p.id} className="card" href={`/projects/${p.id}`} style={{ padding: 12 }}>
                  <div style={{ fontWeight: 700 }}>{p.name || p.id}</div>
                  <div className="small">{p.updated_at ? `Updated: ${p.updated_at}` : ""}</div>
                </a>
              ))}
            </div>
          )}
        </section>

        <section className="card">
          <h2 style={{ margin: 0 }}>Taxonomy</h2>
          <div className="small">Industries → segments → use cases (config-driven).</div>
          <hr />
          <div className="grid">
            {industries.map((ind) => (
              <div key={ind.id} className="card" style={{ padding: 12 }}>
                <div className="hstack" style={{ justifyContent: "space-between" }}>
                  <div>
                    <div style={{ fontWeight: 700 }}>{ind.name}</div>
                    <div className="small">{ind.description || ind.id}</div>
                  </div>
                  <span className="badge">{(ind.segments || []).length} segments</span>
                </div>
              </div>
            ))}
          </div>
          <div className="small" style={{ marginTop: 12 }}>
            Add industries/use-cases by dropping YAML files under <code>registry/taxonomy/</code>.
          </div>
        </section>
      </div>
    </main>
  );
}
