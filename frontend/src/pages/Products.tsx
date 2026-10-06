import { useEffect, useState } from "react";
import { api } from "../api";
import { ProductCard } from "../components/ProductCard";
import { useApp } from "../context/AppContext";
import type { Product } from "../types";

export function Products() {
  const { matched } = useApp();
  const [products, setProducts] = useState<Product[]>([]);
  const [types, setTypes] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [sort, setSort] = useState("featured");
  const [inStockOnly, setInStockOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.garmentTypes().then(setTypes).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const t = setTimeout(() => {
      api
        .listProducts({ search: search || undefined, garment_type: typeFilter || undefined })
        .then(setProducts)
        .catch(() => setProducts([]))
        .finally(() => setLoading(false));
    }, 200);
    return () => clearTimeout(t);
  }, [search, typeFilter]);

  const matchedIds = new Set(matched.map((p) => p.product_id));
  const showMatched =
    matched.length > 0 && !search && !typeFilter && !inStockOnly && sort === "featured";

  function arrange(list: Product[]): Product[] {
    let out = inStockOnly ? list.filter((p) => p.total_stock > 0) : [...list];
    if (sort === "price-asc") out.sort((a, b) => a.price - b.price);
    else if (sort === "price-desc") out.sort((a, b) => b.price - a.price);
    else if (sort === "name") out.sort((a, b) => a.name.localeCompare(b.name));
    return out;
  }
  const shown = arrange(products);

  return (
    <div className="page products">
      <h1>Products</h1>
      <p className="sub">Officially licensed Yale apparel — browse the full rack.</p>

      <div className="filters">
        <input
          placeholder="Search tees, hoodies, colleges, teams…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
          <option value="">All garment types</option>
          {types.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort">
          <option value="featured">Sort: Featured</option>
          <option value="price-asc">Price: low to high</option>
          <option value="price-desc">Price: high to low</option>
          <option value="name">Name: A–Z</option>
        </select>
        <label className="instock-toggle">
          <input
            type="checkbox"
            checked={inStockOnly}
            onChange={(e) => setInStockOnly(e.target.checked)}
          />
          In stock only
        </label>
      </div>

      {showMatched && (
        <>
          <h2 className="matched-head">From your chat</h2>
          <div className="grid">
            {matched.map((p) => (
              <ProductCard key={`m-${p.product_id}`} product={p} />
            ))}
          </div>
          <h2 className="matched-head">Everything else</h2>
        </>
      )}

      {loading ? (
        <p className="empty">Loading the catalogue…</p>
      ) : shown.length === 0 ? (
        <p className="empty">No products matched. Try a different search or filter.</p>
      ) : (
        <div className="grid">
          {shown
            .filter((p) => !(showMatched && matchedIds.has(p.product_id)))
            .map((p) => (
              <ProductCard key={p.product_id} product={p} />
            ))}
        </div>
      )}
    </div>
  );
}
