"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { createQuery, QueryDetail } from "@/lib/api";

interface Props {
  onResult: (result: QueryDetail) => void;
}

export function QueryForm({ onResult }: Props) {
  const queryClient = useQueryClient();
  const [question, setQuestion] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: createQuery,
    onSuccess: (data) => {
      onResult(data);
      queryClient.invalidateQueries({ queryKey: ["queries"] });
      setThreadId(data.thread_id ?? null);
    },
  });

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!question.trim()) {
      return;
    }
    mutation.mutate({ question, thread_id: threadId });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-slate-600" htmlFor="question">
          Question en langage naturel
        </label>
        <textarea
          id="question"
          required
          className="mt-1 w-full rounded-md border border-slate-200 bg-white p-3 shadow-sm focus:border-indigo-500 focus:outline-none"
          rows={4}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ex: Combien de techniciens ont été créés cette semaine ?"
        />
      </div>
      {threadId && (
        <p className="text-xs text-slate-500">
          Conversation suivie avec le thread <span className="font-mono">{threadId}</span>
        </p>
      )}
      <div className="flex items-center gap-3">
        <button
          type="submit"
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-indigo-700 focus:outline-none"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? "Analyse en cours..." : "Lancer la requête"}
        </button>
        {mutation.isError && (
          <span className="text-sm text-red-600">
            {(mutation.error as Error).message}
          </span>
        )}
      </div>
    </form>
  );
}
