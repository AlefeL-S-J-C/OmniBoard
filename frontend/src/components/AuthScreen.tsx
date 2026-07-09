import { useState } from "react";
import { useTranslation } from "react-i18next";

const API = import.meta.env.VITE_API_URL;

interface Props {
  onAuth: (token: string, userId: number, username: string) => void;
}

export default function AuthScreen({ onAuth }: Props) {
  const { t } = useTranslation("auth");
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        const res = await fetch(API + "/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || "Login falhou");
        const data = await res.json();
        onAuth(data.token, data.user_id, data.username);
      } else {
        const res = await fetch(API + "/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || "Registro falhou");
        const data = await res.json();
        onAuth(data.token, data.user_id, data.username);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const startOAuth = (provider: "google" | "github") => {
    window.location.href = `${API}/api/auth/oauth/${provider}`;
  };

  return (
    <div className="w-full max-w-md bg-gray-800 p-6 rounded-lg border border-gray-700">
      <h2 className="text-xl font-bold mb-4 text-center capitalize">{t(mode)} no OmniBoard</h2>
      {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
      <form onSubmit={submit} className="space-y-4">
        {mode === "register" && (
          <div>
            <label className="block text-sm text-gray-400 mb-1">{t("email")}</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>
        )}
        <div>
          <label className="block text-sm text-gray-400 mb-1">{t("username")}</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            minLength={3}
            maxLength={30}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">{t("password")}</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:ring-2 focus:ring-amber-500"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 bg-amber-600 hover:bg-amber-500 disabled:bg-amber-700 text-white font-medium rounded transition-colors"
        >
          {loading ? t("loading") : mode === "login" ? t("login") : t("register")}
        </button>
      </form>
      <p className="mt-4 text-center text-sm text-gray-400">
        {mode === "login" ? t("noAccount") : t("hasAccount")}{" "}
        <button
          onClick={() => setMode((m) => (m === "login" ? "register" : "login"))}
          className="text-amber-400 hover:underline"
        >
          {mode === "login" ? t("signUp") : t("signIn")}
        </button>
      </p>
      <hr className="my-4 border-gray-700" />
      <p className="text-center text-sm text-gray-500">{t("orDev")}</p>
      <button
        onClick={async () => {
          try {
            const res = await fetch(API + "/api/dev-login", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ username: "dev", game_type: "chess", with_ai: true }),
            });
            const data = await res.json();
            onAuth(data.token, data.user_id, data.username);
          } catch {}
        }}
        className="w-full px-3 py-2 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors mb-3"
      >
        {t("devLogin")}
      </button>
      <div className="flex gap-2 justify-center">
        <button
          onClick={() => startOAuth("google")}
          className="flex-1 px-3 py-2 bg-white text-gray-800 rounded hover:bg-gray-100 border border-gray-300 text-sm font-medium"
        >
          Google
        </button>
        <button
          onClick={() => startOAuth("github")}
          className="flex-1 px-3 py-2 bg-gray-900 text-white rounded hover:bg-gray-800 border border-gray-700 text-sm font-medium"
        >
          GitHub
        </button>
      </div>
    </div>
  );
}