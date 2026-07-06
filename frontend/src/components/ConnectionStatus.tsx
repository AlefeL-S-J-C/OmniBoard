interface ConnectionStatusProps {
  status: "disconnected" | "connecting" | "connected" | "error";
  error?: string | null;
}

const STATUS_CONFIG = {
  disconnected: { color: "bg-gray-500", text: "Desconectado" },
  connecting: { color: "bg-yellow-500", text: "Conectando..." },
  connected: { color: "bg-green-500", text: "Conectado" },
  error: { color: "bg-red-500", text: "Erro" },
} as const;

export default function ConnectionStatus({
  status,
  error,
}: ConnectionStatusProps) {
  const config = STATUS_CONFIG[status];
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className={`w-2.5 h-2.5 rounded-full ${config.color}`} />
      <span>{config.text}</span>
      {error && <span className="text-red-400 ml-2">{error}</span>}
    </div>
  );
}
