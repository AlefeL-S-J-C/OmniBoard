export async function fetchDevToken(
  username: string,
  gameType: string = "chess",
  withAi: boolean = true
): Promise<{ token: string; username: string }> {
  const res = await fetch(import.meta.env.VITE_API_URL + "/api/dev-login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, game_type: gameType, with_ai: withAi }),
  });
  if (!res.ok) throw new Error("Falha ao obter token");
  return res.json();
}