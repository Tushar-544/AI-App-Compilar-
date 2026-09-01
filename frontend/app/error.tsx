"use client";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="grid-bg" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "100vh", gap: 16 }}>
      <div style={{ fontSize: 48 }}>⚠</div>
      <h2 style={{ fontSize: 22, fontWeight: 700 }}>Something went wrong</h2>
      <p style={{ color: "var(--text-muted)", fontSize: 14, maxWidth: 400, textAlign: "center" }}>{error.message}</p>
      <button className="btn-primary" onClick={reset}>Try Again</button>
    </div>
  );
}
