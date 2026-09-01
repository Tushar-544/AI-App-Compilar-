"use client";
import { useState } from "react";
import { Copy, Check } from "lucide-react";

const TABS = [
  { key: "intent",       label: "Intent" },
  { key: "architecture", label: "Architecture" },
  { key: "ui_schema",    label: "UI Schema" },
  { key: "api_schema",   label: "API Schema" },
  { key: "db_schema",    label: "DB Schema" },
  { key: "auth_schema",  label: "Auth Schema" },
  { key: "full",         label: "Full Config" },
];

export default function SchemaViewer({ config }: { config: any }) {
  const [activeTab, setActiveTab] = useState("intent");
  const [copied, setCopied] = useState(false);

  const getContent = () => {
    if (activeTab === "full") return config;
    return config[activeTab] || {};
  };

  const json = JSON.stringify(getContent(), null, 2);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(json);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      console.warn("Clipboard API not available");
    }
  };

  return (
    <div className="glass" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.8px" }}>
          Generated Schema
        </div>
        <button className="btn-secondary" onClick={copy} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, padding: "6px 12px" }}>
          {copied ? <><Check size={12} color="var(--green)" /> Copied</> : <><Copy size={12} /> Copy JSON</>}
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {TABS.map((t) => (
          <button key={t.key} className={`tab ${activeTab === t.key ? "active" : ""}`}
            onClick={() => setActiveTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Intent summary cards */}
      {activeTab === "intent" && config.intent && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 8 }}>
          <InfoCard label="App Type"    value={config.intent.app_type} />
          <InfoCard label="Complexity"  value={config.intent.complexity} />
          <InfoCard label="Entities"    value={config.intent.primary_entities?.join(", ")} />
          <InfoCard label="Roles"       value={config.intent.user_roles?.join(", ")} />
        </div>
      )}

      {/* Assumption chips */}
      {activeTab === "intent" && config.intent?.assumptions?.length > 0 && (
        <div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.5px" }}>Assumptions</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {config.intent.assumptions.map((a: string, i: number) => (
              <span key={i} className="badge info">{a}</span>
            ))}
          </div>
        </div>
      )}

      {/* JSON Code */}
      <div className="code-wrap">
        <pre style={{ margin: 0 }}>{json}</pre>
      </div>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div style={{
      background: "var(--bg-primary)", borderRadius: 10, padding: "10px 14px",
      border: "1px solid var(--border)"
    }}>
      <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--accent-light)" }}>{value}</div>
    </div>
  );
}
