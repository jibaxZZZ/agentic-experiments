import "./globals.css";
import type { Metadata } from "next";
import { ReactQueryClientProvider } from "@/components/react-query-provider";

export const metadata: Metadata = {
  title: "SQL Agent Explorer",
  description: "Interroger les bases SQL en langage naturel",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className="min-h-screen bg-slate-50">
        <ReactQueryClientProvider>{children}</ReactQueryClientProvider>
      </body>
    </html>
  );
}
