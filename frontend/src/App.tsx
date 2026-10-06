import { Route, Routes } from "react-router-dom";
import { FloatingChat } from "./components/FloatingChat";
import { NavBar } from "./components/NavBar";
import { About } from "./pages/About";
import { Cart } from "./pages/Cart";
import { Home } from "./pages/Home";
import { Login } from "./pages/Login";
import { ProductDetail } from "./pages/ProductDetail";
import { Products } from "./pages/Products";
import { Signup } from "./pages/Signup";

export default function App() {
  return (
    <div className="app">
      <NavBar />
      <main className="content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:id" element={<ProductDetail />} />
          <Route path="/about" element={<About />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </main>
      <footer className="site-footer">
        <span>Campus Customs · Yale Bulldog Blue · 57 Broadway, New Haven, CT</span>
        <span>Officially licensed Yale merchandise · since 1973</span>
      </footer>
      <FloatingChat />
    </div>
  );
}
