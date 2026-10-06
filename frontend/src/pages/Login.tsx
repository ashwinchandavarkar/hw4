import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, setToken } from "../api";
import { useApp } from "../context/AppContext";

export function Login() {
  const { setUser } = useApp();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const res = await api.login({ email: email.trim(), password });
      setToken(res.token);
      setUser(res.user);
      navigate("/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page auth-page">
      <div className="auth-card">
        <h1>Welcome back</h1>
        <p className="sub">Log in to your Campus Customs account.</p>
        <form onSubmit={submit}>
          <input
            type="email"
            placeholder="you@yale.edu"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <div className="error">{error}</div>
          <button className="btn" type="submit" disabled={busy}>
            {busy ? "Please wait…" : "Log in"}
          </button>
        </form>
        <div className="switch">
          New to Campus Customs? <Link to="/signup">Create an account</Link>
        </div>
      </div>
    </div>
  );
}
