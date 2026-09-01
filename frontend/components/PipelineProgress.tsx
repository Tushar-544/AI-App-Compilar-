"use client";
import { CheckCircle, Loader, XCircle, Clock } from "lucide-react";

interface Stage { id: number; name: string; desc: string; }

export default function PipelineProgress({
  stages, getStatus, loading,
}: {
  stages: Stage[];
  getStatus: (id: number) => string;
  loading: boolean;
}) {
  return (
    <div className="glass" style={{ padding: 20 }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.8px", textTransform: "uppercase", marginBottom: 16 }}>
        Pipeline Progress
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {stages.map((s) => {
          const status = getStatus(s.id);
          return (
            <div key={s.id} style={{
              display: "flex", alignItems: "flex-start", gap: 12,
              padding: "10px 12px", borderRadius: 10,
              background: status === "running" ? "rgba(139,92,246,0.08)" : "transparent",
              border: status === "running" ? "1px solid rgba(139,92,246,0.2)" : "1px solid transparent",
              transition: "all 0.2s"
            }}>
              {/* Icon */}
              <div style={{ marginTop: 1, flexShrink: 0 }}>
                {status === "done"    && <CheckCircle size={16} color="var(--green)" />}
                {status === "running" && <Loader size={16} color="var(--accent)" style={{ animation: "spin 1s linear infinite" }} />}
                {status === "error"   && <XCircle size={16} color="var(--red)" />}
                {status === "idle"    && <Clock size={16} color="var(--text-muted)" />}
              </div>
              <div>
                <div style={{
                  fontSize: 13, fontWeight: 600,
                  color: status === "running" ? "var(--accent-light)"
                       : status === "done"    ? "var(--text-primary)"
                       : "var(--text-muted)"
                }}>
                  {s.id}. {s.name}
                </div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2 }}>{s.desc}</div>
              </div>
            </div>
          );
        })}
      </div>
      {loading && (
        <div style={{ marginTop: 14, fontSize: 12, color: "var(--text-muted)", textAlign: "center", padding: "8px", borderTop: "1px solid var(--border)" }}>
          Running multi-stage pipeline...
        </div>
      )}
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
