import { useState } from "react";
import { fetchDevToken } from "../utils/auth";
import { GAMES } from "../utils/games";

interface DevLoginProps {
  onLogin: (
    matchId: string,
    playerToken: string,
    username: string,
    gameType: string,
    withAi: boolean
  ) => void;
}

export default function DevLogin({ onLogin }: DevLoginProps) {
  const [username, setUsername] = useState("player1");
  const [matchId, setMatchId] = useState("partida_teste");
  const [gameType, setGameType] = useState("chess");
  const [withAi, setWithAi] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { token } = await fetchDevToken(username, gameType, withAi);
      onLogin(matchId, token, username, gameType, withAi);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erro ao conectar ao servidor"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="bg-gray-800 p-8 rounded-xl shadow-2xl max-w-md w-full">
        <h1 className="text-3xl font-bold text-center mb-2">OmniBoard</h1>
        <p className="text-gray-400 text-center mb-8">
          Escolha o jogo e conecte-se
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Jogo</label>
            <div className="grid grid-cols-2 gap-2">
              {GAMES.map((game) => (
                <button
                  key={game.id}
                  type="button"
                  onClick={() => setGameType(game.id)}
                  className={`py-3 px-2 rounded-lg font-medium text-sm transition-colors ${
                    gameType === game.id
                      ? "bg-amber-700 text-white ring-2 ring-amber-400"
                      : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                  }`}
                >
                  {game.name}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={withAi}
                onChange={(e) => setWithAi(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:ring-2 peer-focus:ring-amber-400 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:start-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-700" />
            </label>
            <span className="text-sm text-gray-300">
              Jogar contra IA
            </span>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Nome do Jogador
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-amber-500 focus:outline-none"
              placeholder="Seu nome"
              required
            />
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-1">
              ID da Partida
            </label>
            <input
              type="text"
              value={matchId}
              onChange={(e) => setMatchId(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-amber-500 focus:outline-none"
              placeholder="ID da partida"
              required
            />
          </div>

          {error && (
            <p className="text-red-400 text-sm text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-amber-700 hover:bg-amber-600 disabled:opacity-50 font-bold rounded-lg transition-colors"
          >
            {loading ? "Conectando..." : "Entrar na Partida"}
          </button>
        </form>
      </div>
    </div>
  );
}
