"use client";

import { QueryDetail, fetchQuery } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";

interface Props {
  activeId: string | null;
  initialResult?: QueryDetail | null;
}

export function QueryResult({ activeId, initialResult }: Props) {
  const { data, refetch, status } = useQuery({
    queryKey: ["query", activeId],
    queryFn: () => fetchQuery(activeId as string),
    enabled: Boolean(activeId),
    initialData: initialResult ?? undefined,
  });

  useEffect(() => {
    if (activeId) {
      refetch();
    }
  }, [activeId, refetch]);

  if (!activeId) {
    return <p className="text-sm text-slate-500">Sélectionnez une requête pour afficher les détails.</p>;
  }

  if (status === "pending") {
    return <p className="text-sm text-slate-500">Chargement du résultat...</p>;
  }

  if (status === "error" || !data) {
    return <p className="text-sm text-red-600">Impossible de charger ce résultat.</p>;
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between text-xs uppercase text-slate-500">
          <span>Question</span>
          <span>{new Date(data.created_at).toLocaleString()}</span>
        </div>
        <p className="mt-2 whitespace-pre-line text-slate-700">{data.question}</p>
      </div>

      <div className="rounded-md border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between text-xs uppercase text-slate-500">
          <span>Réponse</span>
          <span className="font-semibold text-indigo-600">{data.status}</span>
        </div>
        {data.response_text ? (
          <p className="mt-2 whitespace-pre-line text-slate-900">{data.response_text}</p>
        ) : (
          <p className="mt-2 text-sm text-slate-500">
            {data.status === "failed"
              ? data.error_message || "Une erreur est survenue."
              : "Aucune réponse disponible."}
          </p>
        )}
        {data.latency_seconds != null && (
          <p className="mt-3 text-xs text-slate-500">
            Latence : {data.latency_seconds.toFixed(2)}s — Thread {data.thread_id ?? "--"}
          </p>
        )}
      </div>
    </div>
  );
}
