import { Link } from "react-router-dom";
import { useApp } from "../context/AppContext";

export function Cart() {
  const { cart, removeFromCart, clearCart } = useApp();
  const total = cart.reduce((sum, i) => sum + i.price * i.quantity, 0);

  if (cart.length === 0) {
    return (
      <div className="page">
        <h1>Your bag</h1>
        <p className="empty">Your bag is empty.</p>
        <Link className="btn" to="/products">
          Browse the catalogue
        </Link>
      </div>
    );
  }

  return (
    <div className="page cart-page">
      <h1>Your bag</h1>
      <p className="sub">Review your Campus Customs picks.</p>

      <div className="cart-list">
        {cart.map((item) => (
          <div className="cart-row" key={`${item.product_id}-${item.size}`}>
            <Link to={`/products/${item.product_id}`} className="cart-thumb">
              <img src={item.image_url} alt={item.name} />
            </Link>
            <div className="cart-info">
              <Link to={`/products/${item.product_id}`} className="cart-name">
                {item.name}
              </Link>
              <span className="cart-meta">
                Size {item.size} · Qty {item.quantity}
              </span>
            </div>
            <div className="cart-price">${(item.price * item.quantity).toFixed(2)}</div>
            <button
              className="btn ghost cart-remove"
              onClick={() => removeFromCart(item.product_id, item.size)}
            >
              Remove
            </button>
          </div>
        ))}
      </div>

      <div className="cart-footer">
        <button className="btn ghost" onClick={clearCart}>
          Clear bag
        </button>
        <div className="cart-total">
          Total: <b>${total.toFixed(2)}</b>
        </div>
      </div>
      <p className="about-note">
        This is a course demo — checkout is not implemented. Prices and stock are
        live from the Campus Customs catalogue.
      </p>
    </div>
  );
}
