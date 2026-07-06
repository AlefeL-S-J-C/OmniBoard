import { useState } from "react";

interface HelpContent {
  title: string;
  objective: string;
  pieces: { symbol: string; name: string; description: string }[];
  rules: string[];
  special: string[];
}

const HELP: Record<string, HelpContent> = {
  chess: {
    title: "Xadrez",
    objective: "Dar xeque-mate no rei adversário.",
    pieces: [
      { symbol: "\u2654", name: "Rei", description: "Move uma casa em qualquer direção. Protegê-lo é o objetivo do jogo." },
      { symbol: "\u2655", name: "Rainha", description: "Move quantas casas quiser em qualquer direção (horizontal, vertical, diagonal)." },
      { symbol: "\u2656", name: "Torre", description: "Move em linha reta (horizontal ou vertical) quantas casas quiser." },
      { symbol: "\u2657", name: "Bispo", description: "Move na diagonal quantas casas quiser. Cada bispo fica em uma cor." },
      { symbol: "\u2658", name: "Cavalo", description: "Move em L (2 casas em uma direção, 1 na perpendicular). Pula sobre peças." },
      { symbol: "\u2659", name: "Peão", description: "Move uma casa para frente. Captura na diagonal. Pode avançar 2 casas no primeiro movimento." },
    ],
    rules: [
      "Clique em uma peça sua para selecionar, depois clique no destino.",
      "Peças brancas começam. Cada jogador move uma peça por turno.",
      "Você não pode capturar suas próprias peças.",
      "O jogo termina quando um rei é capturado (xeque-mate).",
    ],
    special: [
      "Roque: movimento especial do rei com a torre (uma vez por jogo).",
      "En Passant: captura especial de peão ao lado de um peão que avançou 2 casas.",
      "Promoção: peão que chega ao final do tabuleiro vira rainha (ou outra peça).",
    ],
  },
  checkers: {
    title: "Dama",
    objective: "Capturar ou bloquear todas as peças do adversário.",
    pieces: [
      { symbol: "\u2B24", name: "Peça normal", description: "Move uma casa na diagonal para frente. Captura pulando sobre peça adversária." },
      { symbol: "\u25C9", name: "Dama", description: "Peça promovida. Move e captura para frente e para trás na diagonal." },
    ],
    rules: [
      "Clique em uma peça sua e depois no destino.",
      "Peças vermelhas movem para cima, pretas para baixo.",
      "Captura é obrigatória! Se puder capturar, você deve capturar.",
      "Ao chegar na última fileira do oponente, a peça vira Dama.",
    ],
    special: [
      "Captura em cadeia: se após capturar você puder capturar outra, continue.",
      "Damas podem se mover para frente e para trás na diagonal.",
    ],
  },
  reversi: {
    title: "Reversi (Othello)",
    objective: "Terminar a partida com mais peças da sua cor no tabuleiro.",
    pieces: [
      { symbol: "\u2B24", name: "Peça preta", description: "Coloca no tabuleiro para virar peças adversárias." },
      { symbol: "\u25EF", name: "Peça branca", description: "Coloca no tabuleiro para virar peças adversárias." },
    ],
    rules: [
      "Clique em uma posição vazia para colocar sua peça.",
      "Você deve flanquear uma ou mais peças adversárias entre a peça que colocou e outra sua.",
      "Todas as peças adversárias flanqueadas viram para sua cor.",
      "Se não tiver jogadas válidas, o turno passa automaticamente.",
      "A partida termina quando o tabuleiro está cheio ou ninguém pode jogar.",
    ],
    special: [
      "Peças colocadas nos cantos não podem ser viradas.",
      "Controle as bordas e cantos para ter vantagem.",
    ],
  },
  go: {
    title: "Go",
    objective: "Controlar mais território que o adversário.",
    pieces: [
      { symbol: "\u2B24", name: "Pedra preta", description: "Coloca uma pedra preta em uma interseção vazia." },
      { symbol: "\u25EF", name: "Pedra branca", description: "Coloca uma pedra branca em uma interseção vazia." },
    ],
    rules: [
      "Clique em uma interseção para colocar sua pedra.",
      "Pedras do mesmo grupo compartilham liberdades (interseções vazias adjacentes).",
      "Um grupo sem liberdades é capturado e removido do tabuleiro.",
      "Não pode repetir a posição anterior do tabuleiro (regra do Ko).",
      "Passe sua vez clicando em 'Passar'. Quando ambos passam, o jogo termina.",
    ],
    special: [
      "Território é o número de interseções vazias cercadas por suas pedras.",
      "Pedras capturadas contam como pontos para o adversário.",
    ],
  },
  ludo: {
    title: "Ludo",
    objective: "Ser o primeiro a levar todos os 4 peões para o centro do tabuleiro.",
    pieces: [
      { symbol: "\u2B24", name: "Peão", description: "Cada jogador tem 4 peões. Saem da base quando tira 6 no dado." },
    ],
    rules: [
      "Clique em 'Rolar Dado' para jogar o dado.",
      "Com 6, um peão sai da base ou Anda 6 casas e joga novamente.",
      "Sem 6, mova um peão que já está no tabuleiro.",
      "Clique em um peão seu no tabuleiro e depois no destino (automático).",
      "Capturar: se cair em uma casa com peão adversário, ele volta para a base.",
      "Casas seguras (estrelas) protegem contra captura.",
    ],
    special: [
      "Tirar 6 no dado dá direito a jogar novamente.",
      "Se tirar 6 três vezes seguidas, perde a vez.",
      "Para entrar na reta final, o peão precisa do número exato no dado.",
    ],
  },
  trilha: {
    title: "Trilha (Moinho)",
    objective: "Reduzir o adversário a 2 peças ou deixá-lo sem jogadas.",
    pieces: [
      { symbol: "\u25CF", name: "Peça branca", description: "Coloca no tabuleiro para formar moinhos e capturar peças adversárias." },
      { symbol: "\u25CB", name: "Peça preta", description: "Coloca no tabuleiro para formar moinhos e capturar peças adversárias." },
    ],
    rules: [
      "Fase 1: cada jogador coloca 9 peças alternadamente no tabuleiro.",
      "Fase 2: após colocar todas, mova uma peça por vez para posição adjacente.",
      "Fase 3: com 3 peças, pode voar para qualquer posição vazia.",
      "Formar um moinho (3 peças em linha) permite remover uma peça adversária.",
      "Clique em uma posição vazia para colocar ou mover sua peça.",
    ],
    special: [
      "Moinho: três peças em linha reta (horizontal ou vertical).",
      "Remover: ao formar um moinho, clique em uma peça adversária para remover.",
      "Não pode remover peças de um moinho adversário a menos que todas estejam em moinhos.",
    ],
  },
};

interface GameHelpProps {
  gameType: string;
}

export default function GameHelp({ gameType }: GameHelpProps) {
  const [open, setOpen] = useState(false);
  const help = HELP[gameType];
  if (!help) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={() => setOpen(!open)}
        className="w-10 h-10 rounded-full bg-amber-700 hover:bg-amber-600 font-bold text-lg flex items-center justify-center shadow-lg"
        title="Ajuda"
      >
        ?
      </button>

      {open && (
        <div className="absolute bottom-12 right-0 w-80 max-h-[80vh] overflow-y-auto bg-gray-800 border border-gray-600 rounded-xl shadow-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold">{help.title}</h2>
            <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-white text-xl">&times;</button>
          </div>

          <p className="text-sm text-gray-300 mb-3">
            <span className="text-amber-400 font-medium">Objetivo:</span> {help.objective}
          </p>

          <div className="mb-3">
            <h3 className="text-sm font-semibold text-gray-400 mb-1">Peças</h3>
            <div className="space-y-1">
              {help.pieces.map((p, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-gray-300">
                  <span className="text-lg flex-shrink-0">{p.symbol}</span>
                  <div>
                    <span className="font-medium text-gray-200">{p.name}:</span> {p.description}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mb-3">
            <h3 className="text-sm font-semibold text-gray-400 mb-1">Regras</h3>
            <ul className="space-y-1">
              {help.rules.map((r, i) => (
                <li key={i} className="text-xs text-gray-300 flex gap-2">
                  <span className="text-amber-500 flex-shrink-0">{i + 1}.</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>

          {help.special.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-1">Especiais</h3>
              <ul className="space-y-1">
                {help.special.map((s, i) => (
                  <li key={i} className="text-xs text-gray-300 flex gap-2">
                    <span className="text-blue-400 flex-shrink-0">&rarr;</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
