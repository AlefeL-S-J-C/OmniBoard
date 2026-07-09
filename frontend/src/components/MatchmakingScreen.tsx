import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL;

interface Props {
  token: string;
  onMatch: (matchId: string, gameType: string, withAi: boolean) => void;
  onBack: () => void;
}

export default function MatchmakingScreen({ token, onMatch, onBack }: Props) {
  const [gameType, setGameType] = useState("chess");
  const [withAi, setWithAi] = useState(false);
  const [searching, setSearching] = useState(false);
  const [status, setStatus] = useState<"idle" | "searching" | "matched">("idle");
  const [pollInterval, setPollInterval] = useState<number | null>(null);

  const startSearch = async () => {
    setSearching(true);
    setStatus("searching");
    const res = await fetch(API + "/api/matchmaking/join", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ game_type: gameType, with_ai: withAi }),
    });
    const data = await res.json();
    if (data.matched) {
      setStatus("matched");
      onMatch(data.match_id, gameType, withAi);
    } else {
      // start polling
      const interval = window.setInterval(poll, 2000);
      setPollInterval(interval);
    }
  };

  const poll = async () => {
    const res = await fetch(API + "/api/matchmaking/join", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ game_type: gameType, with_ai: withAi }),
    });
    const data = await res.json();
    if (data.matched) {
      if (pollInterval) clearInterval(pollInterval);
      setStatus("matched");
      onMatch(data.match_id, gameType, withAi);
    }
  };

  const cancelSearch = () => {
    if (pollInterval) clearInterval(pollInterval);
    setSearching(false);
    setStatus("idle");
  };

  useEffect(() => () => {
    if (pollInterval) clearInterval(pollInterval);
  }, [pollInterval]);

  return (
    <div className="w-full max-w-md bg-gray-800 p-6 rounded-lg border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Procurar Partida</h2>
        <button
          onClick={onBack}
          className="text-gray-400 hover:text-white text-sm"
        >
          ← Voltar
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">Jogo</label>
          <select
            value={gameType}
            onChange={(e) => setGameType(e.target.value)}
            disabled={searching}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50"
          >
            <option value="chess">Xadrez</option>
            <option value="checkers">Dama</option>
            <option value="go">Go</option>
            <option value="ludo">Ludo</option>
            <option value="trilha">Trilha</option>
            <option value="reversi">Reversi</option>
          </select>
        </div>

        <label className="flex items-center gap-2 text-sm text-gray-300">
          <input
            type="checkbox"
            checked={withAi}
            onChange={(e) => setWithAi(e.target.checked)}
            disabled={searching}
            className="accent-amber-500"
          />
          Jogar contra IA (instantâneo)
        </label>

        {!searching ? (
          <button
            onClick={startSearch}
            className="w-full py-2 bg-amber-600 hover:bg-amber-500 text-white font-medium rounded transition-colors"
          >
            Entrar na Fila
          </button>
        ) : (
          <div className="space-y-2">
            <p className="text-center text-gray-300">
              {status === "searching" ? "Procurando oponente..." : "Partida encontrada!"}
            </p>
            <div className="flex justify-center">
              <div className="w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
            </div>
            <button
              onClick={cancelSearch}
              className="w-full py-2 bg-gray-700 hover:bg-gray-600 text-white font-medium rounded transition-colors"
            >
              Cancelar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}