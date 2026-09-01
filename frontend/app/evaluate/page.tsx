"use client";
import { useState } from "react";
import { BarChart2, Play, CheckCircle, XCircle, Wrench, ChevronLeft } from "lucide-react";
import Link from "next/link";

export default function EvaluatePage() {
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const runEval = async () => {
    setRunning(true);
    setResults(null);
    setError(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      if (!res.ok) {
        const errBody = await res.text();
        let detail = `Server error (${res.status})`;
        try { detail = JSON.parse(errBody).detail || detail; } catch {}
        throw new Error(detail);
      }
      const data = await res.json();
      setResults(data);
    } catch (e: any) {
      setError(e.message || "Evaluation failed");
      console.error(e);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="grid-bg min-h-screen" style={{ padding: "32px 24px", maxWidth: 1200, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 32 }}>
        <Link href="/" style={{ color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 4, textDecoration: "none", fontSize: 13 }}>
          <ChevronLeft size={16} /> Back
        </Link>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <BarChart2 size={22} color="var(--accent)" />
          <h1 style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.5px" }}>
            <span className="gradient-text">Evaluation Framework</span>
          </h1>
        </div>
        <span className="badge info">20 Prompts · 10 Real + 10 Edge Cases</span>
      </div>

      {/* Action */}
      <div className="glass" style={{ padding: 24, marginBottom: 24, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>Run Full Evaluation Suite</div>
          <div style={{ fontSize: 13, color: "var(--text-muted)" }}>Tests 10 real product prompts + 10 edge cases. Tracks success rate, latency, cost, retries, and repair actions.</div>
        </div>
        <button className="btn-primary" onClick={runEval} disabled={running}
          style={{ display: "flex", alignItems: "center", gap: 8, whiteSpace: "nowrap" }}>
          {running ? (
            <><span style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} /> Running...</>
          ) : (
            <><Play size={15} /> Run All 20 Prompts</>
          )}
        </button>
      </div>

      {error && (
        <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 12, padding: 16, marginBottom: 20, color: "var(--red)", fontSize: 14 }}>
          ⚠ {error}
        </div>
      )}

      {/* Summary cards */}
      {results?.summary && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(6,1fr)", gap: 12, marginBottom: 24 }}>
          <SummaryCard label="Success Rate" value={`${results.summary.success_rate}%`} color="var(--green)" />
          <SummaryCard label="Passed" value={results.summary.success} color="var(--green)" />
          <SummaryCard label="Failed" value={results.summary.failed} color={results.summary.failed > 0 ? "var(--red)" : "var(--green)"} />
          <SummaryCard label="Avg Latency" value={`${(results.summary.avg_latency_ms/1000).toFixed(1)}s`} color="var(--accent-light)" />
          <SummaryCard label="Total Cost" value={`$${results.summary.total_cost_usd}`} color="var(--yellow)" />
          <SummaryCard label="Total Repairs" value={results.summary.total_repairs} color="var(--yellow)" />
        </div>
      )}

      {/* Results table */}
      {results?.results && (
        <div className="glass" style={{ padding: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 16 }}>
            Detailed Results
          </div>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)", fontSize: 11, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                  {["ID", "Label", "Status", "Latency", "Cost", "Repairs", "Issues"].map(h => (
                    <th key={h} style={{ padding: "8px 12px", textAlign: "left", fontWeight: 600 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.results.map((r: any, i: number) => (
                  <tr key={r.id} style={{
                    borderBottom: "1px solid var(--border)",
                    background: i % 2 === 0 ? "transparent" : "rgba(255,255,255,0.01)"
                  }}>
                    <td style={{ padding: "10px 12px", color: "var(--text-muted)", fontFamily: "JetBrains Mono, monospace", fontSize: 11 }}>{r.id}</td>
                    <td style={{ padding: "10px 12px", fontWeight: 500 }}>{r.label}</td>
                    <td style={{ padding: "10px 12px" }}>
                      {r.success
                        ? <span className="badge success"><CheckCircle size={10} /> Pass</span>
                        : <span className="badge error"><XCircle size={10} /> Fail</span>}
                    </td>
                    <td style={{ padding: "10px 12px", color: "var(--text-secondary)" }}>{(r.latency_ms/1000).toFixed(1)}s</td>
                    <td style={{ padding: "10px 12px", color: "var(--text-secondary)" }}>${r.cost_usd?.toFixed(4)}</td>
                    <td style={{ padding: "10px 12px" }}>
                      {r.repair_actions?.length > 0
                        ? <span className="badge warn"><Wrench size={10} /> {r.repair_actions.length}</span>
                        : <span style={{ color: "var(--text-muted)" }}>0</span>}
                    </td>
                    <td style={{ padding: "10px 12px", color: "var(--text-muted)" }}>{r.validation_issues}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

function SummaryCard({ label, value, color }: { label: string; value: any; color: string }) {
  return (
    <div className="metric-card">
      <div style={{ fontSize: 22, fontWeight: 800, color, marginBottom: 4 }}>{value}</div>
      <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px" }}>{label}</div>
    </div>
  );
}
