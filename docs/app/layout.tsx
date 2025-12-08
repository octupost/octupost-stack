import "./globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Media Agent API Explorer",
  description: "Filterable explorer for media generation and editing APIs"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="bg-surface">
      <body className="bg-surface text-slate-200 min-h-screen">
        {children}
      </body>
    </html>
  );
}

