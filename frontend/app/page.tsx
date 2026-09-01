"use client";
import { useState } from "react";
import PipelineProgress from "@/components/PipelineProgress";
import SchemaViewer from "@/components/SchemaViewer";
import MetricsSidebar from "@/components/MetricsSidebar";
import { Zap, ExternalLink, BarChart2 } from "lucide-react";
import Link from "next/link";

const EXAMPLE_PROMPTS = [
  "Build a CRM with login, contacts, deals pipeline, role-based access for admin and sales reps, analytics dashboard, and Stripe payments.",
  "Create an LMS where instructors create courses with videos and quizzes, students track progress, and admins manage the platform.",
  "Build a project management tool like Trello with boards, tasks, team collaboration, file uploads, and role-based permissions.",
];

const STAGES = [
  { id: 1, name: "Intent Extraction",  desc: "Parse natural language → structured intent" },
  { id: 2, name: "System Design",      desc: "Design app architecture & entity relationships" },
  { id: 3, name: "Schema Generation",  desc: "Generate UI · API · DB · Auth schemas (parallel)" },
  { id: 4, name: "Refinement",         desc: "Resolve cross-layer inconsistencies" },
  { id: 5, name: "Validation & Repair",desc: "Detect issues · surgical auto-repair" },
];

export default function Home() {
  const [prompt, setPrompt]     = useState("");
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState<any>(null);
  const [events, setEvents]     = useState<any[]>([]);
  const [error, setError]       = useState<string | null>(null);

  const stageStatus = (stageId: number) => {
    const ev = events.find((e) => e.stage === stageId);
    if (!ev) return "idle";
    return ev.status; // "running" | "done" | "error"
  };

  const generate = async () => {
    if (!prompt.trim() || loading) return;
    setLoading(true);
    setResult(null);
    setEvents([]);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'}/generate/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        const errBody = await response.text();
        let detail = `Server error (${response.status})`;
        try { detail = JSON.parse(errBody).detail || detail; } catch {}
        throw new Error(detail);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) throw new Error("Failed to open stream");

      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.status === "error") throw new Error(data.detail);
              
              setEvents(prev => {
                const existing = prev.find(e => e.stage === data.stage);
                if (existing) {
                  return prev.map(e => e.stage === data.stage ? data : e);
                }
                return [...prev, data];
              });

              if (data.config) {
                setResult(data.config);
                try {
                  localStorage.setItem("compilar_preview_config", JSON.stringify(data.config));
                } catch {}
              }
            } catch (parseErr: any) {
              if (parseErr.message && !parseErr.message.includes("JSON")) throw parseErr;
              console.warn("SSE parse skip:", parseErr);
            }
          }
        }
      }
    } catch (e: any) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid-bg min-h-screen">
      {/* Nav */}
      <nav style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "16px 32px", borderBottom: "1px solid var(--border)",
        backdropFilter: "blur(12px)", position: "sticky", top: 0, zIndex: 50,
        background: "rgba(7,7,15,0.8)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 10,
            background: "linear-gradient(135deg,#7c3aed,#8b5cf6)",
            display: "flex", alignItems: "center", justifyContent: "center"
          }}>
            <Zap size={18} color="white" />
          </div>
          <span style={{ fontWeight: 700, fontSize: 18, letterSpacing: "-0.5px" }}>
            <span className="gradient-text">Compilar</span>
          </span>
          <span style={{
            fontSize: 11, fontWeight: 600, padding: "2px 8px",
            background: "var(--accent-glow)", border: "1px solid var(--border-glow)",
            borderRadius: 999, color: "var(--accent-light)", marginLeft: 4
          }}>AI App Compiler</span>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <Link href="/evaluate" style={{ color: "var(--text-secondary)", fontSize: 14, textDecoration: "none", display: "flex", alignItems: "center", gap: 6 }}>
            <BarChart2 size={15} /> Evaluation
          </Link>
          <Link href="/preview" style={{ color: "var(--text-secondary)", fontSize: 14, textDecoration: "none", display: "flex", alignItems: "center", gap: 6 }}>
            <Zap size={15} /> Preview
          </Link>
          <a href="https://github.com" target="_blank" rel="noopener" style={{ color: "var(--text-secondary)", display: "flex", alignItems: "center" }}>
            <ExternalLink size={18} />
          </a>
        </div>
      </nav>

      <main style={{ maxWidth: 1280, margin: "0 auto", padding: "40px 24px" }}>

        {/* Hero */}
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <h1 style={{ fontSize: 52, fontWeight: 800, letterSpacing: "-2px", lineHeight: 1.1, marginBottom: 16 }}>
            Natural Language<br />
            <span className="gradient-text">→ Working App Config</span>
          </h1>
          <p style={{ color: "var(--text-secondary)", fontSize: 17, maxWidth: 560, margin: "0 auto" }}>
            A 5-stage AI compiler that converts your idea into validated, executable UI · API · DB · Auth schemas.
          </p>
        </div>

        {/* Input area */}
        <div className="glass" style={{ padding: 24, marginBottom: 28 }}>
          <label style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)", display: "block", marginBottom: 10, letterSpacing: "0.5px", textTransform: "uppercase" }}>
            App Description
          </label>
          <textarea
            className="prompt-input"
            placeholder='e.g. "Build a CRM with login, contacts, deals pipeline, analytics, and Stripe payments..."'
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) generate(); }}
          />

          {/* Examples */}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 12, marginBottom: 16 }}>
            {EXAMPLE_PROMPTS.map((p, i) => (
              <button key={i} className="btn-secondary" style={{ fontSize: 12, padding: "5px 12px" }}
                onClick={() => setPrompt(p)}>
                Example {i + 1}
              </button>
            ))}
          </div>

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
              {prompt.length} chars · Ctrl+Enter to submit
            </span>
            <button className="btn-primary" onClick={generate} disabled={loading || !prompt.trim()}
              style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {loading ? (
                <><span style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", display: "inline-block", animation: "spin 0.7s linear infinite" }} />
                Compiling...</>
              ) : (
                <><Zap size={16} /> Compile App</>
              )}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 12, padding: 16, marginBottom: 20, color: "var(--red)", fontSize: 14 }}>
            ⚠ {error}
          </div>
        )}

        {/* Pipeline Progress + Results */}
        <div style={{ display: "grid", gridTemplateColumns: loading || result ? "300px 1fr" : "1fr", gap: 20 }}>

          {/* Left: Pipeline */}
          {(loading || result) && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <PipelineProgress stages={STAGES} getStatus={stageStatus} loading={loading} />
              {result && <MetricsSidebar metadata={result.metadata} />}
            </div>
          )}

          {/* Right: Schema output */}
          {result && (
            <SchemaViewer config={result} />
          )}

          {/* Idle state — pipeline diagram */}
          {!loading && !result && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 12 }}>
              {STAGES.map((s, i) => (
                <div key={s.id} className="glass glass-hover" style={{ padding: 20, position: "relative" }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: 10,
                    background: "var(--accent-glow)", border: "1px solid var(--border-glow)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 15, fontWeight: 700, color: "var(--accent-light)",
                    marginBottom: 12
                  }}>{s.id}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>{s.name}</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 }}>{s.desc}</div>
                  {i < 4 && (
                    <div style={{ position: "absolute", right: -10, top: "50%", color: "var(--text-muted)", fontSize: 18, zIndex: 1 }}>›</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
