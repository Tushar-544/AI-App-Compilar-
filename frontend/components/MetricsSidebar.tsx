"use client";
import { Clock, DollarSign, Wrench, AlertTriangle, CheckCircle } from "lucide-react";

export default function MetricsSidebar({ metadata }: { metadata: any }) {
  if (!metadata) return null;
  const { total_latency_ms, cost_estimate_usd, repair_actions, validation_issues, total_retries } = metadata;

  return (
    <div className="glass" style={{ padding: 20 }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.8px", textTransform: "uppercase", marginBottom: 14 }}>
        Pipeline Metrics
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <MetricRow icon={<Clock size={14} color="var(--accent)" />}   label="Latency"   value={`${(total_latency_ms ? total_latency_ms/1000 : 0).toFixed(1)}s`} />
        <MetricRow icon={<DollarSign size={14} color="var(--green)" />} label="Est. Cost" value={`$${cost_estimate_usd?.toFixed(4)}`} />
        <MetricRow icon={<Wrench size={14} color="var(--yellow)" />}  label="Repairs"   value={repair_actions?.length || 0} highlight={repair_actions?.length > 0} />
        <MetricRow icon={<AlertTriangle size={14} color="var(--yellow)" />} label="Issues" value={Array.isArray(validation_issues) ? validation_issues.length : (validation_issues || 0)} />
        <MetricRow icon={<CheckCircle size={14} color="var(--green)" />} label="Retries" value={total_retries || 0} />
      </div>

      {/* Repair actions list */}
      {repair_actions?.length > 0 && (
        <div style={{ marginTop: 14, borderTop: "1px solid var(--border)", paddingTop: 14 }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.5px" }}>Auto-Repairs</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
            {repair_actions.map((r: string, i: number) => (
              <div key={i} style={{ fontSize: 11, color: "var(--yellow)", background: "rgba(245,158,11,0.08)", borderRadius: 6, padding: "4px 8px", lineHeight: 1.4 }}>
                ✦ {r}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MetricRow({ icon, label, value, highlight }: { icon: any; label: string; value: any; highlight?: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 7, color: "var(--text-muted)", fontSize: 12 }}>
        {icon} {label}
      </div>
      <span style={{
        fontSize: 13, fontWeight: 700,
        color: highlight ? "var(--yellow)" : "var(--text-primary)"
      }}>{value}</span>
    </div>
  );
}
