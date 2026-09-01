import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Compilar — AI App Compiler",
  description: "Convert natural language into validated, executable app configurations. Multi-stage AI pipeline.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
