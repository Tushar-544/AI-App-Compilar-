"use client";
import { useState, useEffect, Suspense } from "react";
import { Monitor, ChevronLeft } from "lucide-react";
import Link from "next/link";

// A mock runtime that renders the app config as a working-looking UI
function RuntimePreviewInner() {
  const [config, setConfig] = useState<any>(null);
  const [activePage, setActivePage] = useState<any>(null);

  // Accept config from localStorage (set by main page) or use a demo
  useEffect(() => {
    try {
      const stored = localStorage.getItem("compilar_preview_config");
      if (stored) {
        const c = JSON.parse(stored);
        setConfig(c);
        setActivePage(c.ui_schema?.pages?.[0]);
      }
    } catch (e) {
      console.error("Failed to load preview config:", e);
    }
  }, []);

  if (!config) return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "60vh", gap: 16 }}>
      <Monitor size={48} color="var(--text-muted)" />
      <div style={{ color: "var(--text-muted)", fontSize: 15 }}>Generate an app first, then come back here to preview it.</div>
      <Link href="/" className="btn-primary" style={{ textDecoration: "none" }}>← Go Generate</Link>
    </div>
  );

  const { ui_schema, api_schema, db_schema, auth_schema, intent } = config;
  const pages = ui_schema?.pages || [];

  return (
    <div style={{ display: "flex", height: "calc(100vh - 64px)", overflow: "hidden" }}>
      {/* Sidebar nav */}
      <div style={{
        width: 220, background: "var(--bg-secondary)", borderRight: "1px solid var(--border)",
        padding: "20px 12px", display: "flex", flexDirection: "column", gap: 4, overflowY: "auto"
      }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: "var(--accent-light)", padding: "0 8px 12px", letterSpacing: "0.5px" }}>
          {ui_schema?.brand_name || intent?.app_name}
        </div>
        {pages.map((p: any) => (
          <button key={p.id}
            onClick={() => setActivePage(p)}
            style={{
              display: "flex", alignItems: "center", gap: 8, padding: "9px 10px",
              borderRadius: 8, border: "none", cursor: "pointer", textAlign: "left",
              background: activePage?.id === p.id ? "var(--accent-glow)" : "transparent",
              color: activePage?.id === p.id ? "var(--accent-light)" : "var(--text-muted)",
              fontSize: 13, fontWeight: activePage?.id === p.id ? 600 : 400,
              transition: "all 0.15s", fontFamily: "Inter, sans-serif"
            }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "currentColor", flexShrink: 0 }} />
            {p.title}
            {p.is_premium && <span className="badge info" style={{ fontSize: 9, padding: "1px 5px" }}>PRO</span>}
          </button>
        ))}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, overflowY: "auto", padding: 28, background: "var(--bg-primary)" }}>
        {activePage ? (
          <>
            <div style={{ marginBottom: 24 }}>
              <h2 style={{ fontSize: 22, fontWeight: 700 }}>{activePage.title}</h2>
              <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
                Access: {activePage.access?.join(", ")} · Layout: {activePage.layout}
                {activePage.is_premium && <span className="badge info" style={{ marginLeft: 8 }}>Premium</span>}
              </div>
            </div>

            {/* Render components */}
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {activePage.components?.map((comp: any) => (
                <ComponentRenderer key={comp.id} comp={comp} dbTables={db_schema?.tables || []} />
              ))}
            </div>
          </>
        ) : (
          <div style={{ color: "var(--text-muted)" }}>Select a page from the sidebar</div>
        )}
      </div>

      {/* Right panel — schema details */}
      <div style={{
        width: 260, background: "var(--bg-secondary)", borderLeft: "1px solid var(--border)",
        padding: 16, overflowY: "auto"
      }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 12 }}>DB Tables</div>
        {db_schema?.tables?.map((t: any) => (
          <div key={t.name} style={{ marginBottom: 12, background: "var(--bg-card)", borderRadius: 8, padding: 10, border: "1px solid var(--border)" }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "var(--accent-light)", marginBottom: 6 }}>{t.entity}</div>
            {t.columns?.slice(0, 4).map((c: any) => (
              <div key={c.name} style={{ fontSize: 10, color: "var(--text-muted)", padding: "2px 0" }}>
                <span style={{ color: "var(--text-secondary)" }}>{c.name}</span>
                <span style={{ marginLeft: 6, color: "var(--text-muted)", fontFamily: "JetBrains Mono" }}>{c.type}</span>
              </div>
            ))}
            {t.columns?.length > 4 && <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>+{t.columns.length - 4} more</div>}
          </div>
        ))}

        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 12, marginTop: 16 }}>Auth Roles</div>
        {auth_schema?.roles?.map((r: string) => (
          <span key={r} className="badge info" style={{ marginRight: 6, marginBottom: 6, display: "inline-block" }}>{r}</span>
        ))}

        <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.8px", marginBottom: 12, marginTop: 16 }}>API Endpoints</div>
        <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{api_schema?.endpoints?.length || 0} endpoints defined</div>
      </div>
    </div>
  );
}

function ComponentRenderer({ comp, dbTables }: { comp: any; dbTables: any[] }) {
  const table = dbTables.find(t => 
    t.entity?.toLowerCase() === comp.entity?.toLowerCase() ||
    t.name?.toLowerCase() === comp.entity?.toLowerCase() ||
    t.entity?.toLowerCase() === comp.entity?.replace(/s$/, '')?.toLowerCase()
  );

  if (comp.type === "DataTable") {
    return (
      <div className="glass" style={{ padding: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12 }}>{comp.label || comp.entity} Table</div>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--text-muted)" }}>
              {table?.columns?.slice(0, 5).map((c: any) => (
                <th key={c.name} style={{ padding: "6px 10px", textAlign: "left", fontWeight: 500 }}>{c.name}</th>
              )) || <th style={{ padding: "6px 10px" }}>{comp.entity}</th>}
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3].map(i => (
              <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                {table?.columns?.slice(0, 5).map((c: any) => (
                  <td key={c.name} style={{ padding: "8px 10px", color: "var(--text-muted)" }}>— mock —</td>
                )) || <td style={{ padding: "8px 10px", color: "var(--text-muted)" }}>row {i}</td>}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (comp.type === "Form") {
    return (
      <div className="glass" style={{ padding: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12 }}>{comp.label || "Form"}</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          {table?.columns?.slice(1, 5).map((c: any) => (
            <div key={c.name}>
              <label style={{ fontSize: 11, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>{c.name}</label>
              <input readOnly placeholder={c.type} style={{
                width: "100%", background: "var(--bg-primary)", border: "1px solid var(--border)",
                borderRadius: 8, padding: "7px 10px", color: "var(--text-secondary)", fontSize: 12,
                fontFamily: "Inter, sans-serif", outline: "none"
              }} />
            </div>
          )) || <div style={{ color: "var(--text-muted)", fontSize: 12 }}>Form fields here</div>}
        </div>
        <button className="btn-primary" style={{ marginTop: 14, fontSize: 13, padding: "8px 20px" }}>Submit</button>
      </div>
    );
  }

  if (comp.type === "Stat" || comp.type === "Chart") {
    return (
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
        {["Total Records", "Active Users", "Revenue", "Growth"].map((label, i) => (
          <div key={i} className="metric-card">
            <div style={{ fontSize: 22, fontWeight: 800, color: "var(--accent-light)", marginBottom: 4 }}>
              {["1,284", "892", "$24.5k", "+12%"][i]}
            </div>
            <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{label}</div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="glass" style={{ padding: 14, display: "flex", alignItems: "center", gap: 10 }}>
      <span className="badge info">{comp.type}</span>
      <span style={{ fontSize: 13, color: "var(--text-muted)" }}>{comp.label || comp.id}</span>
    </div>
  );
}

export default function PreviewPage() {
  return (
    <div className="grid-bg min-h-screen">
      <nav style={{
        display: "flex", alignItems: "center", gap: 16, padding: "14px 24px",
        borderBottom: "1px solid var(--border)", background: "rgba(7,7,15,0.9)"
      }}>
        <Link href="/" style={{ color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 4, textDecoration: "none", fontSize: 13 }}>
          <ChevronLeft size={16} /> Back
        </Link>
        <Monitor size={18} color="var(--accent)" />
        <span style={{ fontWeight: 700, fontSize: 16 }}><span className="gradient-text">Runtime Preview</span></span>
        <span className="badge info">Execution Awareness Demo</span>
      </nav>
      <Suspense fallback={<div style={{ padding: 40, color: "var(--text-muted)" }}>Loading...</div>}>
        <RuntimePreviewInner />
      </Suspense>
    </div>
  );
}
