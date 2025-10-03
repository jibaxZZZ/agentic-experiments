"use client";

import { useQuery } from "@tanstack/react-query";
import { QueryRecord, fetchQueries } from "@/lib/api";

interface Props {
  onSelect: (id: string) => void;
  activeId?: string | null;
}

export function QueryHistory({ onSelect, activeId }: Props) {
  const { data, status, fetchStatus } = useQuery({
    queryKey: ["queries"],
    queryFn: fetchQueries,
    refetchInterval: 15000,
  });

  if (status === "pending" && fetchStatus === "fetching") {
    return <HistorySkeleton />;
  }

  if (status === "error") {
    return <p className="text-sm text-red-600">Impossible de charger l'historique.</p>;
  }

  if (!data || data.length === 0) {
    return <p className="text-sm text-slate-500">Aucune requête enregistrée pour le moment.</p>;
  }

  return (
    <ul className="space-y-2">
      {data.map((record) => (
        <li key={record.id}>
          <button
            onClick={() => onSelect(record.id)}
            className={`w-full rounded-md border p-3 text-left text-sm shadow-sm transition hover:border-indigo-400 ${
              activeId === record.id
                ? "border-indigo-500 bg-indigo-50"
                : "border-slate-200 bg-white"
            }`}
          >
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>{new Date(record.created_at).toLocaleString()}</span>
              <span className="font-semibold uppercase text-indigo-600">{record.status}</span>
            </div>
            <p className="mt-1 line-clamp-2 text-slate-700">{record.question}</p>
          </button>
        </li>
      ))}
    </ul>
  );
}

function HistorySkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="h-16 w-full animate-pulse rounded-md bg-slate-200" />
      ))}
    </div>
  );
}
