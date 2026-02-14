"use client";

import { useEffect, useMemo, useState } from "react";
import { createProject, fetchIndustries, fetchPacks } from "../../lib/api";

type SelectedPack = { domain: string; pack_id: string; version: string };

function latestVersion(versions: string[]) {
  return [...versions].sort().slice(-1)[0] || "";
}

export default function NewProjectPage() {
  const [industries, setIndustries] = useState<any[]>([]);
  const [packs, setPacks] = useState<any[]>([]);
  const [err, setErr] = useState<string | null>(null);

  const [name, setName] = useState("My AI System");
  const [description, setDescription] = useState("");

  const [industryId, setIndustryId] = useState<string>("");
  const [segmentId, setSegmentId] = useState<string>("");
  const [useCaseId, setUseCaseId] = useState<string>("");

  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [selectedPacks, setSelectedPacks] = useState<Record<string, SelectedPack>>({}); // key=domain/pack_id

  useEffect(() => {
    (async () => {
      try {
        const [i, p] = await Promise.all([fetchIndustries(), fetchPacks()]);
        setIndustries(i.industries || []);
        setPacks(p.packs || []);
      } catch (e: any) {
        setErr(e.message || String(e));
      }
    })();
  }, []);

  const segments = useMemo(() => {
    const ind = industries.find((x) => x.id === industryId);
    return ind?.segments || [];
  }, [industries, industryId]);

  const useCases = useMemo(() => {
    const seg = segments.find((x: any) => x.id === segmentId);
    return seg?.use_cases || [];
  }, [segments, segmentId]);

  const useCase = useMemo(() => useCases.find((x: any) => x.id === useCaseId), [useCases, useCaseId]);

  useEffect(() => {
    // reset downstream selections when parent changes
    setSegmentId("");
    setUseCaseId("");
    setAnswers({});
  }, [industryId]);

  useEffect(() => {
    setUseCaseId("");
    setAnswers({});
  }, [segmentId]);

  useEffect(() => {
    if (!useCase) return;
    const defaults: Record<string, any> = {};
    for (const q of (useCase.scope_questions || [])) {
      if (q.default !== undefined) defaults[q.id] = q.default;
    }
    setAnswers(defaults);
  }, [useCaseId]); // eslint-disable-line react-hooks/exhaustive-deps

  function togglePack(domain: string, pack_id: string, versions: string[]) {
    const k = `${domain}/${pack_id}`;
    setSelectedPacks((prev) => {
      const next = {...prev};
      if (next[k]) delete next[k];
      else next[k] = { domain, pack_id, version: latestVersion(versions) };
      return next;
    });
  }

  function setPackVersion(domain: string, pack_id: string, version: string) {
    const k = `${domain}/${pack_id}`;
    setSelectedPacks((prev) => ({...prev, [k]: { domain, pack_id, version }}));
  }

  async function onCreate() {
    setErr(null);
    try {
      const payload = {
        name,
        description: description || null,
        industry_id: industryId,
        segment_id: segmentId,
        use_case_id: useCaseId,
        scope_answers: answers,
        selected_packs: Object.values(selectedPacks),
      };
      const res = await createProject(payload);
      const id = res.project_id;
      window.location.href = `/projects/${id}`;
    } catch (e: any) {
      setErr(e.message || String(e));
    }
  }

  const canCreate = industryId && segmentId && useCaseId && Object.values(selectedPacks).length > 0;

  return (
    <main className="container">
      <div className="card">
        <h2 style={{marginTop:0}}>Create Project</h2>
        <div className="small">
          Choose a use case, answer scoping questions, pick packs, and generate an audit-ready checklist.
        </div>

        {err && (
          <div className="card" style={{ marginTop: 12, borderColor: "#fecaca", background: "#fff1f2" }}>
            <div style={{ fontWeight: 700 }}>Error</div>
            <div className="small">{err}</div>
          </div>
        )}

        <hr />

        <div className="grid grid2">
          <div>
            <label>Project name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} />
            <label>Description (optional)</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
          </div>

          <div>
            <label>Industry</label>
            <select value={industryId} onChange={(e) => setIndustryId(e.target.value)}>
              <option value="">Select…</option>
              {industries.map((ind) => (
                <option key={ind.id} value={ind.id}>{ind.name}</option>
              ))}
            </select>

            <label>Segment</label>
            <select value={segmentId} onChange={(e) => setSegmentId(e.target.value)} disabled={!industryId}>
              <option value="">Select…</option>
              {segments.map((seg: any) => (
                <option key={seg.id} value={seg.id}>{seg.name}</option>
              ))}
            </select>

            <label>Use case</label>
            <select value={useCaseId} onChange={(e) => setUseCaseId(e.target.value)} disabled={!segmentId}>
              <option value="">Select…</option>
              {useCases.map((uc: any) => (
                <option key={uc.id} value={uc.id}>{uc.name}</option>
              ))}
            </select>
          </div>
        </div>

        {useCase && (
          <>
            <hr />
            <h3 style={{marginTop:0}}>Scope</h3>
            <div className="small">{useCase.description}</div>
            <div className="grid grid2" style={{marginTop:8}}>
              {(useCase.scope_questions || []).map((q: any) => (
                <div key={q.id}>
                  <label>{q.prompt}</label>
                  {q.type === "boolean" && (
                    <select value={String(answers[q.id] ?? false)} onChange={(e) => setAnswers(a => ({...a, [q.id]: e.target.value === "true"}))}>
                      <option value="true">Yes</option>
                      <option value="false">No</option>
                    </select>
                  )}
                  {q.type === "select" && (
                    <select value={answers[q.id] ?? ""} onChange={(e) => setAnswers(a => ({...a, [q.id]: e.target.value}))}>
                      {(q.options || []).map((opt: string) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  )}
                  {q.type === "multiselect" && (
                    <select
                      multiple
                      value={answers[q.id] ?? []}
                      onChange={(e) => {
                        const vals = Array.from(e.target.selectedOptions).map(o => o.value);
                        setAnswers(a => ({...a, [q.id]: vals}));
                      }}
                      size={Math.min(5, (q.options || []).length || 3)}
                    >
                      {(q.options || []).map((opt: string) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  )}
                  {q.type === "string" && (
                    <input value={answers[q.id] ?? ""} onChange={(e) => setAnswers(a => ({...a, [q.id]: e.target.value}))} />
                  )}
                  {q.type === "number" && (
                    <input type="number" value={answers[q.id] ?? ""} onChange={(e) => setAnswers(a => ({...a, [q.id]: Number(e.target.value)}))} />
                  )}
                </div>
              ))}
            </div>
          </>
        )}

        <hr />
        <h3 style={{marginTop:0}}>Select Packs</h3>
        <div className="small">Choose one or more packs across Security/Safety/Governance.</div>

        <div className="grid" style={{marginTop:12}}>
          {packs.map((p) => {
            const k = `${p.domain}/${p.pack_id}`;
            const checked = Boolean(selectedPacks[k]);
            const versions: string[] = p.versions || [];
            return (
              <div key={k} className="card" style={{padding:12}}>
                <div className="hstack" style={{justifyContent:"space-between"}}>
                  <div>
                    <div style={{fontWeight:700}}>{p.pack_id}</div>
                    <div className="small"><span className="badge">{p.domain}</span> {versions.length} version(s)</div>
                  </div>
                  <button className={"btn " + (checked ? "btnDanger" : "btnPrimary")} onClick={() => togglePack(p.domain, p.pack_id, versions)}>
                    {checked ? "Remove" : "Add"}
                  </button>
                </div>
                {checked && (
                  <div style={{marginTop:10}}>
                    <label>Version</label>
                    <select value={selectedPacks[k].version} onChange={(e) => setPackVersion(p.domain, p.pack_id, e.target.value)}>
                      {versions.map((v) => <option key={v} value={v}>{v}</option>)}
                    </select>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <hr />
        <div className="hstack" style={{justifyContent:"space-between"}}>
          <div className="small">
            {canCreate ? "Ready to generate a checklist." : "Select a use case and at least one pack."}
          </div>
          <button className={"btn " + (canCreate ? "btnPrimary" : "")} disabled={!canCreate} onClick={onCreate}>
            Generate Checklist
          </button>
        </div>
      </div>
    </main>
  );
}
