"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchChecklist, fetchProject, patchChecklistItem, reportUrl, uploadEvidence } from "../../../lib/api";

const STATUS = ["not_started", "in_progress", "implemented", "not_applicable", "risk_accepted"];

function sevBadge(sev: string) {
  const styles: Record<string, React.CSSProperties> = {
    critical: { borderColor: "#fecaca", background: "#fff1f2", color: "#7f1d1d" },
    high: { borderColor: "#fed7aa", background: "#fff7ed", color: "#7c2d12" },
    medium: { borderColor: "#bfdbfe", background: "#eff6ff", color: "#1e3a8a" },
    low: { borderColor: "#e2e8f0", background: "#f8fafc", color: "#0f172a" }
  };
  return <span className="badge" style={styles[sev] || {}}>{sev}</span>;
}

export default function ProjectPage({ params }: { params: { projectId: string } }) {
  const projectId = params.projectId;
  const [project, setProject] = useState<any | null>(null);
  const [checklist, setChecklist] = useState<any | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  async function refresh() {
    setErr(null);
    try {
      const [p, c] = await Promise.all([fetchProject(projectId), fetchChecklist(projectId)]);
      setProject(p);
      setChecklist(c);
    } catch (e: any) {
      setErr(e.message || String(e));
    }
  }

  useEffect(() => { refresh(); }, [projectId]); // eslint-disable-line react-hooks/exhaustive-deps

  const counts = checklist?.counts || {};
  const items: any[] = checklist?.items || [];

  const progress = useMemo(() => {
    const total = counts.total || items.length || 0;
    const implemented = (counts.by_status?.implemented) || items.filter(i => i.status === "implemented").length;
    return total ? Math.round((implemented / total) * 100) : 0;
  }, [counts, items]);

  async function updateItem(itemId: string, patch: any) {
    setBusy(itemId);
    try {
      await patchChecklistItem(projectId, itemId, patch);
      await refresh();
    } catch (e: any) {
      setErr(e.message || String(e));
    } finally {
      setBusy(null);
    }
  }

  async function onUpload(itemId: string, file: File) {
    setBusy(itemId);
    try {
      await uploadEvidence(projectId, itemId, file);
      await refresh();
    } catch (e: any) {
      setErr(e.message || String(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <main className="container">
      <div className="card">
        <div className="hstack" style={{justifyContent:"space-between"}}>
          <div>
            <div style={{fontWeight:800, fontSize:18}}>{project?.project?.name || projectId}</div>
            <div className="small">
              Use case: <code>{project?.inputs?.use_case_id}</code> · Packs: {(project?.inputs?.selected_packs || []).length}
            </div>
          </div>
          <div className="hstack">
            <a className="btn" href={reportUrl(projectId, "html")} target="_blank">View Report (HTML)</a>
            <a className="btn" href={reportUrl(projectId, "csv")} target="_blank">Export CSV</a>
            <a className="btn" href={reportUrl(projectId, "pdf")} target="_blank">Export PDF</a>
          </div>
        </div>

        {err && (
          <div className="card" style={{ marginTop: 12, borderColor: "#fecaca", background: "#fff1f2" }}>
            <div style={{ fontWeight: 700 }}>Error</div>
            <div className="small">{err}</div>
          </div>
        )}

        <hr />
        <div className="hstack">
          <span className="badge">Progress: {progress}%</span>
          <span className="badge">Total: {counts.total ?? items.length}</span>
          {counts.by_domain && Object.entries(counts.by_domain).map(([d, n]: any) => (
            <span key={d} className="badge">{d}: {n}</span>
          ))}
        </div>
      </div>

      <div className="card" style={{marginTop:16}}>
        <div className="hstack" style={{justifyContent:"space-between"}}>
          <h2 style={{margin:0}}>Checklist</h2>
          <button className="btn" onClick={refresh}>Refresh</button>
        </div>
        <div className="small">Update status/owner/notes and attach evidence per control.</div>

        <div style={{overflow:"auto", marginTop:12, maxHeight:"68vh"}}>
          <table>
            <thead>
              <tr>
                <th>Domain</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Control</th>
                <th>Owner</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it) => (
                <tr key={it.item_id}>
                  <td><span className="badge">{it.domain}</span></td>
                  <td>{sevBadge(it.severity)}</td>
                  <td style={{minWidth:170}}>
                    <select
                      value={it.status}
                      disabled={busy === it.item_id}
                      onChange={(e) => updateItem(it.item_id, { status: e.target.value })}
                    >
                      {STATUS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </td>
                  <td style={{minWidth:380}}>
                    <div style={{fontWeight:700}}>{it.title}</div>
                    <div className="small">{it.objective}</div>
                    {it.why_applies && <details style={{marginTop:8}}>
                      <summary className="small">Why it applies</summary>
                      <pre className="small" style={{whiteSpace:"pre-wrap"}}>{it.why_applies}</pre>
                    </details>}
                    <details style={{marginTop:8}}>
                      <summary className="small">Expected evidence</summary>
                      <ul className="small">
                        {(it.evidence_required || []).map((e: any, idx: number) => (
                          <li key={idx}>{e.type} — {e.name}</li>
                        ))}
                      </ul>
                    </details>
                  </td>
                  <td style={{minWidth:220}}>
                    <input
                      value={it.owner || ""}
                      placeholder="Owner"
                      disabled={busy === it.item_id}
                      onChange={(e) => updateItem(it.item_id, { owner: e.target.value })}
                    />
                    <textarea
                      style={{marginTop:8}}
                      rows={3}
                      placeholder="Notes / implementation record"
                      value={it.notes || ""}
                      disabled={busy === it.item_id}
                      onChange={(e) => updateItem(it.item_id, { notes: e.target.value })}
                    />
                  </td>
                  <td style={{minWidth:240}}>
                    <div className="small">{(it.evidence || []).length} file(s)</div>
                    <input
                      type="file"
                      disabled={busy === it.item_id}
                      onChange={(e) => {
                        const f = e.target.files?.[0];
                        if (f) onUpload(it.item_id, f);
                      }}
                    />
                    <ul className="small">
                      {(it.evidence || []).slice(0, 3).map((ev: any) => (
                        <li key={ev.sha256}>{ev.file_name} <span style={{opacity:0.7}}>({ev.sha256.slice(0,10)}…)</span></li>
                      ))}
                      {(it.evidence || []).length > 3 && <li>…</li>}
                    </ul>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={6} className="small">No controls generated. Adjust packs/scoping.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
