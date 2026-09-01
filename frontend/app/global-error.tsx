"use client";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html>
      <body style={{ background: "#07070f", color: "#f0f0ff", fontFamily: "Inter, sans-serif", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "100vh", gap: 16 }}>
        <div style={{ fontSize: 48 }}>⚠</div>
        <h2 style={{ fontSize: 22, fontWeight: 700 }}>Something went wrong</h2>
        <p style={{ color: "#4a4a6a", fontSize: 14, maxWidth: 400, textAlign: "center" }}>{error.message}</p>
        <button onClick={reset} style={{ background: "linear-gradient(135deg, #7c3aed, #8b5cf6)", color: "white", border: "none", borderRadius: 12, padding: "12px 28px", fontWeight: 600, fontSize: 15, cursor: "pointer" }}>Try Again</button>
      </body>
    </html>
  );
}
