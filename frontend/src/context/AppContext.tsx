import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api, getToken, setToken } from "../api";
import type { CartItem, Product, PublicUser } from "../types";

const CART_KEY = "cc_cart";

function loadCart(): CartItem[] {
  try {
    const raw = localStorage.getItem(CART_KEY);
    return raw ? (JSON.parse(raw) as CartItem[]) : [];
  } catch {
    return [];
  }
}

interface AppState {
  user: PublicUser | null;
  setUser: (u: PublicUser | null) => void;
  logout: () => void;
  /** Products the chat agent has surfaced, shown across the app. */
  matched: Product[];
  setMatched: (p: Product[]) => void;
  /** Shopping bag (persisted to localStorage). */
  cart: CartItem[];
  cartCount: number;
  addToCart: (item: CartItem) => void;
  removeFromCart: (product_id: string, size: string) => void;
  clearCart: () => void;
}

const Ctx = createContext<AppState | undefined>(undefined);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<PublicUser | null>(null);
  const [matched, setMatched] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>(loadCart);

  useEffect(() => {
    if (getToken()) {
      api
        .me()
        .then(setUser)
        .catch(() => setToken(null));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
  }, [cart]);

  const value = useMemo<AppState>(
    () => ({
      user,
      setUser,
      logout: () => {
        setToken(null);
        setUser(null);
      },
      matched,
      setMatched,
      cart,
      cartCount: cart.reduce((n, i) => n + i.quantity, 0),
      addToCart: (item) =>
        setCart((prev) => {
          const idx = prev.findIndex(
            (i) => i.product_id === item.product_id && i.size === item.size
          );
          if (idx >= 0) {
            const next = [...prev];
            next[idx] = { ...next[idx], quantity: next[idx].quantity + item.quantity };
            return next;
          }
          return [...prev, item];
        }),
      removeFromCart: (product_id, size) =>
        setCart((prev) =>
          prev.filter((i) => !(i.product_id === product_id && i.size === size))
        ),
      clearCart: () => setCart([]),
    }),
    [user, matched, cart]
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useApp(): AppState {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
