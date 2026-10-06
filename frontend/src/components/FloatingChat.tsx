import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import type { ChatMessage, Product } from "../types";

const GREETING: ChatMessage = {
  role: "assistant",
  content:
    "Hi! I'm the Campus Customs assistant. Tell me what you're after — a hoodie, " +
    "your residential college, a team, a gift for a Yale parent — and I'll pull up " +
    "matching gear with live prices and sizes. Boola Boola! 🐶",
};

/** Floating bottom-right chat. Connected to the live agent backend. */
export function FloatingChat() {
  const { user, setMatched } = useApp();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [panelProducts, setPanelProducts] = useState<Product[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  // The product detail page the shopper is viewing, if any (e.g. /products/abc).
  const productMatch = location.pathname.match(/^\/products\/(.+)$/);
  const currentProductId = productMatch ? decodeURIComponent(productMatch[1]) : undefined;

  // On login, reload saved history; on logout, reset to a fresh greeting.
  useEffect(() => {
    if (!user) {
      setMessages([GREETING]);
      setPanelProducts([]);
      return;
    }
    api
      .chatHistory()
      .then((turns) => {
        if (turns.length === 0) {
          setMessages([GREETING]);
          return;
        }
        setMessages([GREETING, ...turns.map((t) => ({ role: t.role, content: t.content }))]);
        const lastWithProducts = [...turns].reverse().find((t) => t.products.length > 0);
        if (lastWithProducts) setPanelProducts(lastWithProducts.products);
      })
      .catch(() => setMessages([GREETING]));
  }, [user]);

  useEffect(() => {
    if (open) endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, open]);

  async function sendText(raw: string) {
    const text = raw.trim();
    if (!text || loading) return;

    const history = messages.filter((m) => m !== GREETING);
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    setError("");

    try {
      const res = await api.chat(text, history, currentProductId);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
      if (res.products.length > 0) {
        setPanelProducts(res.products);
        setMatched(res.products); // surface across the app (e.g. Products page)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry — I hit a snag reaching the shop. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function send(e: React.FormEvent) {
    e.preventDefault();
    void sendText(input);
  }

  return (
    <>
      {!open && (
        <button className="chat-fab" onClick={() => setOpen(true)} aria-label="Open chat">
          💬 Ask us
        </button>
      )}

      {open && (
        <section className="chat-float" role="dialog" aria-label="Campus Customs chat">
          <div className="chat-head">
            <div className="chat-head-id">
              <div className="chat-avatar" aria-hidden="true">🐶</div>
              <div>
                <h3>Dan, your shop guide</h3>
                <p>Live catalogue — real prices &amp; sizes.</p>
              </div>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              ✕
            </button>
          </div>

          <div className="messages">
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                {m.content}
              </div>
            ))}

            {panelProducts.length > 0 && (
              <div className="chat-products">
                {panelProducts.slice(0, 6).map((p) => (
                  <Link
                    key={p.product_id}
                    className="chat-product"
                    to={`/products/${p.product_id}`}
                    onClick={() => setOpen(false)}
                    title={`View ${p.name}`}
                  >
                    <img src={p.image_url} alt={p.name} />
                    <div className="mini">
                      <span className="mini-name">{p.name}</span>
                      <span className="mini-brief">{p.garment_type}</span>
                      <span className="mini-row">
                        <span className="mini-price">${p.price.toFixed(2)}</span>
                        <span className={`mini-stock ${p.total_stock > 0 ? "in" : "out"}`}>
                          {p.total_stock > 0 ? "In stock" : "Out of stock"}
                        </span>
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}

            {loading && (
              <div className="msg assistant pending">
                <span className="typing" aria-label="typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {messages.length <= 1 && !loading && (
            <div className="chat-suggestions">
              {["Show me hoodies", "Residential college gear", "Gift for a Yale dad", "Something under $40"].map(
                (s) => (
                  <button key={s} className="chip" onClick={() => sendText(s)}>
                    {s}
                  </button>
                )
              )}
            </div>
          )}

          {error && <div className="error" style={{ padding: "0 12px" }}>{error}</div>}

          <form className="chat-form" onSubmit={send}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g. navy hoodie under $70"
              disabled={loading}
              aria-label="Message"
            />
            <button className="btn" type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
    </>
  );
}
