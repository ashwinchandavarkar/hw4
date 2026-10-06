import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { useApp } from "../context/AppContext";
import type { Product } from "../types";

const SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"];

export function ProductDetail() {
  const { id } = useParams<{ id: string }>();
  const { addToCart } = useApp();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [selectedSize, setSelectedSize] = useState("");
  const [added, setAdded] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setNotFound(false);
    setSelectedSize("");
    setAdded(false);
    api
      .getProduct(id)
      .then(setProduct)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="page"><p className="empty">Loading…</p></div>;
  if (notFound || !product)
    return (
      <div className="page">
        <p className="empty">Product not found.</p>
        <Link className="btn ghost" to="/products">
          ← Back to products
        </Link>
      </div>
    );

  const sizes = [...product.inventory].sort(
    (a, b) => SIZE_ORDER.indexOf(a.size) - SIZE_ORDER.indexOf(b.size)
  );

  return (
    <div className="page detail">
      <Link className="back-link" to="/products">
        ← Back to products
      </Link>

      <div className="detail-grid">
        <div className="detail-img">
          <img src={product.image_url} alt={product.name} />
        </div>

        <div className="detail-info">
          <h1>{product.name}</h1>
          <div className="type">{product.garment_type}</div>
          <div className="detail-price">${product.price.toFixed(2)}</div>

          <p className="detail-desc">{product.description}</p>

          {product.colors.length > 0 && (
            <p className="detail-colors">
              <b>Colors:</b> {product.colors.join(", ")}
            </p>
          )}

          <h3>Sizes &amp; availability</h3>
          {sizes.length > 0 ? (
            <table className="size-table">
              <thead>
                <tr>
                  <th>Size</th>
                  <th>In stock</th>
                </tr>
              </thead>
              <tbody>
                {sizes.map((s) => (
                  <tr key={s.size} className={s.quantity > 0 ? "" : "sold"}>
                    <td>{s.size}</td>
                    <td>{s.quantity > 0 ? `${s.quantity} available` : "Sold out"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="empty">Size information is not available for this item.</p>
          )}

          <div className={`stock ${product.total_stock > 0 ? "in" : "out"}`}>
            {product.total_stock > 0
              ? `${product.total_stock} total in stock`
              : "Currently out of stock"}
          </div>

          {product.total_stock > 0 && (
            <div className="add-to-bag">
              <label>
                Size
                <select
                  value={selectedSize}
                  onChange={(e) => {
                    setSelectedSize(e.target.value);
                    setAdded(false);
                  }}
                >
                  <option value="">Choose a size</option>
                  {sizes.map((s) => (
                    <option key={s.size} value={s.size} disabled={s.quantity === 0}>
                      {s.size}
                      {s.quantity === 0 ? " — sold out" : ""}
                    </option>
                  ))}
                </select>
              </label>
              <button
                className="btn"
                disabled={!selectedSize}
                onClick={() => {
                  addToCart({
                    product_id: product.product_id,
                    name: product.name,
                    price: product.price,
                    image_url: product.image_url,
                    size: selectedSize,
                    quantity: 1,
                  });
                  setAdded(true);
                }}
              >
                Add to Bag
              </button>
              {added && (
                <span className="added-note">
                  Added size {selectedSize} to your bag ✓
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
