import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL;

export default function ReplayPanel({ matchId, gameType }: { matchId: string; gameType: string }) {
  const [events, setEvents] = useState<any[]>([]);
  const [idx, setIdx] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/matches/${matchId}/events`)
      .then(r => r.json())
      .then(data => {
        setEvents(data);
        setIdx(data.length - 1);
        setLoading(false);
      });
  }, [matchId]);

  if (loading) return <p className="text-gray-400 text-center">Carregando histórico…</p>;
  if (!events.length) return <p className="text-gray-400 text-center">Sem lances.</p>;

  const cur = events[idx];
  const go = (delta: number) => setIdx(i => Math.max(0, Math.min(events.length - 1, i + delta)));

  return (
    <div className="mt-6 w-full max-w-[640px] bg-gray-800 p-4 rounded-lg border border-gray-700">
      <h3 className="font-bold mb-2">Replay – {gameType}</h3>
      <div className="flex items-center gap-4 mb-2">
        <button onClick={() => go(-1)} disabled={idx === 0}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 rounded">← Anterior</button>
        <span className="flex-1 text-center text-sm">
          Lance {idx + 1} / {events.length} – {cur.player}
        </span>
        <button onClick={() => go(1)} disabled={idx === events.length - 1}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 rounded">Próximo →</button>
      </div>

      <div className="aspect-square">
        <pre className="bg-gray-900 p-2 rounded text-xs overflow-auto max-h-64">
          {JSON.stringify(cur.state, null, 2)}
        </pre>
      </div>
    </div>
  );
}