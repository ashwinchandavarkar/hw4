import { Link, NavLink } from "react-router-dom";
import { useApp } from "../context/AppContext";

export function NavBar() {
  const { user, logout, cartCount } = useApp();

  return (
    <header className="topbar">
      <Link to="/" className="brand">
        <span className="mark">CAMPUS CUSTOMS</span>
        <span className="tag">Yale Bulldog Blue · since 1973</span>
      </Link>

      <nav className="nav">
        <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
          Home
        </NavLink>
        <NavLink to="/products" className={({ isActive }) => (isActive ? "active" : "")}>
          Products
        </NavLink>
        <NavLink to="/about" className={({ isActive }) => (isActive ? "active" : "")}>
          About Us
        </NavLink>
      </nav>

      <div className="spacer" />

      <NavLink to="/cart" className="bag-link" aria-label="Shopping bag">
        🛍️ Bag
        {cartCount > 0 && <span className="bag-badge">{cartCount}</span>}
      </NavLink>

      {user ? (
        <>
          <span className="user-chip">
            Hey, <b>{user.first_name || user.name}</b>
          </span>
          <button className="btn ghost" onClick={logout}>
            Log out
          </button>
        </>
      ) : (
        <div className="nav-auth">
          <NavLink to="/login" className="btn ghost">
            Log in
          </NavLink>
          <NavLink to="/signup" className="btn">
            Create account
          </NavLink>
        </div>
      )}
    </header>
  );
}
