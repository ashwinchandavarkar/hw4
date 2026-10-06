import { Link } from "react-router-dom";
import type { Product } from "../types";

function shorten(text: string, max = 90): string {
  if (text.length <= max) return text;
  return text.slice(0, max).trimEnd() + "…";
}

export function ProductCard({ product }: { product: Product }) {
  return (
    <Link className="card" to={`/products/${product.product_id}`}>
      <div className="imgwrap">
        <img src={product.image_url} alt={product.name} loading="lazy" />
      </div>
      <div className="body">
        <div className="name">{product.name}</div>
        <div className="type">{product.garment_type}</div>
        <p className="desc">{shorten(product.description)}</p>
        <div className="row">
          <span className="price">${product.price.toFixed(2)}</span>
          <span className={`stock ${product.total_stock > 0 ? "in" : "out"}`}>
            {product.total_stock > 0 ? "In stock" : "Out of stock"}
          </span>
        </div>
      </div>
    </Link>
  );
}
