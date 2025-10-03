'use client';

import { Suspense, useState } from "react";
import { QueryForm } from "@/components/query-form";
import { QueryHistory } from "@/components/query-history";
import { QueryResult } from "@/components/query-result";
import { QueryDetail } from "@/lib/api";

export default function Home() {
  const [activeId, setActiveId] = useState<string | null>(null);
  const [latestResult, setLatestResult] = useState<QueryDetail | null>(null);

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <header className="mb-8 flex flex-col gap-2">
        <h1 className="text-3xl font-bold text-slate-900">SQL Agent Explorer</h1>
        <p className="text-sm text-slate-500">
          Interrogez vos bases Postgres / MySQL via le serveur MCP en langage naturel.
        </p>
      </header>

      <div className="grid gap-8 lg:grid-cols-[2fr_1fr]">
        <section className="space-y-6">
          <QueryForm
            onResult={(data) => {
              setActiveId(data.id);
              setLatestResult(data);
            }}
          />
          <div className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
            <Suspense fallback={<p>Chargement des résultats...</p>}>
              <QueryResult activeId={activeId} initialResult={latestResult} />
            </Suspense>
          </div>
        </section>

        <aside className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-800">Historique</h2>
          <p className="mb-4 text-xs text-slate-500">
            Les requêtes sont persistées dans Postgres par le backend FastAPI.
          </p>
          <Suspense fallback={<p>Chargement...</p>}>
            <QueryHistory
              onSelect={(id) => {
                setActiveId(id);
              }}
              activeId={activeId}
            />
          </Suspense>
        </aside>
      </div>
    </main>
  );
}
